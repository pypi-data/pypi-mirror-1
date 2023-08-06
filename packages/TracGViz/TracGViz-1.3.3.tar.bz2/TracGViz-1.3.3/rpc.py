#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

r"""RPC handlers not included in TracXmlRpcPlugin and used to 
implement some data providers supporting Google Visualization API
protocol.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

__all__ = 'TimelineRPC', 'ReportRPC', 'VersionControlRPC'

from trac.core import implements, ExtensionPoint, Component
from trac.mimeview.api import Mimeview, Context
from trac.ticket.report import ReportModule
from trac.ticket.query import Query, QuerySyntaxError
from trac.timeline.api import ITimelineEventProvider
from trac.timeline.web_ui import TimelineModule
from trac.util.datefmt import _epoc
from trac.util.translation import _
from trac.versioncontrol.api import RepositoryManager, NoSuchNode, \
                                    NoSuchChangeset
from trac.versioncontrol.web_ui.browser import CHUNK_SIZE 
from trac.web.href import Href

from datetime import datetime, date, time
from fnmatch import fnmatch
from itertools import imap
from os.path import splitext
from tracrpc.api import IXMLRPCHandler
import types
from urlparse import urlunparse, urlparse
import xmlrpclib

from util import get_column_desc, rpc_to_datetime, rpc_opt_sigs

__metaclass__ = type

#--------------------------------------------------
#   Event Timeline RPC
#--------------------------------------------------

class TimelineRPC(Component):
    r""" An interface to Trac's timeline module.
    """ 
    implements(IXMLRPCHandler)
    sources = ExtensionPoint(ITimelineEventProvider)

    def __init__(self):
        self._event_data = TimelineModule(self.env)._event_data
    
    # IXMLRPCHandler methods
    def xmlrpc_namespace(self):
        return 'timeline'
    
    def xmlrpc_methods(self):
        yield ('TIMELINE_VIEW', 
                ((list, xmlrpclib.DateTime, xmlrpclib.DateTime, list),
                 (list, xmlrpclib.DateTime, xmlrpclib.DateTime), 
                 (list, xmlrpclib.DateTime), 
                 (list, )), 
                 self.getEvents)
        yield ('TIMELINE_VIEW', ((list,),), self.getEventFilters)

    STMT = "(kind, author, date, dateuid, " \
            "unicode(render('url', ctx)).encode('utf-8', 'replace'), " \
            "unicode(render('title', ctx)).encode('utf-8', 'replace'), " \
            "unicode(render('description', ctx)).encode('utf-8', 'replace'))"
    STMT = compile(STMT, '<string>', 'eval')
    
    # Exported methods
    def getEvents(self, req, start=None, stop=None, filters=None):
        r"""Retrieve events taking place in a time window.
        
        @param start    initial date in time interval
        @param stop     last date in time interval
        @param filter   is a list of the enabled filters, 
                        each item being the name (first item) in the 
                        tuples returned by 
                        `ITimelineEventProvider.get_timeline_filters`. 
                        If none is specified then all available 
                        filters will be used.
        @return         a list of events in the time range given by 
                        the `start` and `stop` parameters. Each item 
                        is represented as a tuple of the form 
                        (kind, author, date, timestamp, url, title, desc) 
                        representing information about each event.
        
        
        Note: In order to retrieve all events related to ticket 
              changes (e.g. attachments) you need to set
              timeline.ticket_show_details option in trac.ini to true.
        """
        if start is None:
            start = _epoc
        else:
            start = rpc_to_datetime(start, req)
        if stop is None:
            stop = datetime.now(req.tz)
        else:
            stop = rpc_to_datetime(stop, req)
        if filters is None:
            filters = list(f for f, _ in self.getEventFilters(req))
        ctx = Context.from_request(req, absurls=True)
        globs = dict(ctx=ctx)
        return list(eval(self.STMT, globs, self._event_data(p, e)) \
                                for p in self.sources \
                                for e in p.get_timeline_events(req, \
                                            start, stop, filters))
    
    def getEventFilters(self, req):
        r"""Return a list of the filters available to retrieve events 
        provided  by the timeline module. The data returned for each 
        filter is a binary tuple containing the filter 
        name as well as its display name.
        """
        fdata = dict(fi[:2] for p in self.sources \
                        for fi in p.get_timeline_filters(req))
        return fdata.iteritems()

#--------------------------------------------------
#   Ticket Report RPC
#--------------------------------------------------

class ReportRPC(Component):
    r""" An interface to Trac's report module.
    """ 
    implements(IXMLRPCHandler)
    
    def __init__(self):
      self.repmdl = ReportModule(self.env)
    
    # IXMLRPCHandler methods
    def xmlrpc_namespace(self):
        return 'report'
    
    def xmlrpc_methods(self):
        yield ('REPORT_VIEW', ((list,),), self.getAll)
        yield ('REPORT_VIEW', ((dict, int),), self.get)
        yield ('REPORT_VIEW', ((dict, int),), self.execute)
        yield ('REPORT_VIEW', ((list, int),), self.enum_columns)

    # Exported methods
    def getAll(self, req):
        r"""Return a list containing the IDs of all available reports.
        """
        # Copycat ! I really did nothing
        db = self.env.get_db_cnx()
        sql = ("SELECT id FROM report ORDER BY id")
        cursor = db.cursor()
        try:
          cursor.execute(sql)
          result = cursor.fetchall() or []
          return (x[0] for x in result)
        finally:
          cursor.close()
    
    def get(self, req, id):
        r"""Return information about an specific report as a dict 
        containing the following fields.
        
        - id :            the report ID.
        - title:          the report title.
        - description:    the report description.
        - query:          the query string used to select the tickets 
                          to be included in this report
        """
        sql = "SELECT id,title,query,description from report " \
                 "WHERE id=%s" % (id,)
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        try:
          cursor.execute(sql)
          for report_info in cursor:
              return dict(zip(['id','title','query','description'], report_info))
          else:
              return None
        finally:
          cursor.close()
    
    def _execute_sql(self, req, id, sql, limit=0):
        r"""Execute a SQL report and return no more than `limit` rows 
        (or all rows if limit == 0).
        """
        repmdl = self.repmdl
        db = self.env.get_db_cnx()
        try:
          args = repmdl.get_var_args(req)
        except ValueError,e:
          raise ValueError(_('Report failed: %(error)s', error=e))
        try:
            try:
              # Paginated exec (>=0.11)
              exec_proc = repmdl.execute_paginated_report
              kwargs = dict(limit=limit)
            except AttributeError:
              # Legacy exec (<=0.10)
              exec_proc = repmdl.execute_report
              kwargs = {}
            return exec_proc(req, db, id, sql, args, **kwargs)[:2]
        except Exception, e:
            db.rollback()
            raise 
    
    def execute(self, req, id):
        r"""Execute a Trac report.
        
        @param id     the report ID.
        @return       a list containing the data provided by the 
                      target report.
        @throws       NotImplementedError if the report definition 
                      consists of saved custom query specified 
                      using a URL.
        @throws       QuerySyntaxError if the report definition 
                      consists of a TracQuery containing syntax errors.
        @throws       Exception in case of detecting any other error.
        """
        sql = self.get(req, id)['query']
        query = ''.join([line.strip() for line in sql.splitlines()])
        if query and (query[0] == '?' or query.startswith('query:?')):
          raise NotImplementedError('Saved custom queries specified ' \
                                  'using URLs are not supported.')
        elif query.startswith('query:'):
          query = Query.from_string(self.env, query[6:], report=id)
          server_url = urlparse(req.base_url)
          server_href = Href(urlunparse((server_url.scheme, \
                                        server_url.netloc, \
                                        '', '', '', '')))
          def rel2abs(row):
            """Turn relative value in 'href' into absolute URLs."""
            self.log.debug('IG: Query Row %s', row)
            row['href'] = server_href(row['href'])
            return row
            
          return imap(rel2abs, query.execute(req))
        else:
          cols, results = self._execute_sql(req, id, sql)
          return (dict(zip(cols, list(row))) for row in results)
    
    def _sql_cursor(self, req, db, id, sql, args, limit=0, offset=0):
      r"""Retrieve a cursor to access the data returned by a SQL 
      report.
      """
      # Copycat ! ReportModule.execute_paginated_report
      # I didnt want to but I had no other choice :(
      repmdl = self.repmdl
      sql, args = repmdl.sql_sub_vars(sql, args, db)
      if not sql:
          raise ValueError(_('Report %(num)s has no SQL query.', num=id))
      self.log.debug('IG: Executing report with SQL "%s"' % sql)
      self.log.debug('IG: Request args: %r' % req.args)
      cursor = db.cursor()
      
      # The column name is obtained.
      get_col_name_sql = 'SELECT * FROM ( ' + sql + ' ) AS tab LIMIT 1'
      cursor.execute(get_col_name_sql, args)
      self.env.log.debug("IG: Query SQL(Get col names): " + get_col_name_sql)
      return cursor
    
    def _sql_columns(self, req, id, sql):
      r"""Retrieve the description of columns returned by a SQL 
      report.
      """
      repmdl = self.repmdl
      db = self.env.get_db_cnx()
      try:
        args = repmdl.get_var_args(req)
      except ValueError,e:
        raise ValueError(_('Report failed: %(error)s', error=e))
      try:
          cursor = self._sql_cursor(req, db, id, sql, args)
      except Exception, e:
          db.rollback()
          raise 
      else:
        self.log.debug('IG: Cursor desc %s', cursor.description)
        cols = list(get_column_desc(cursor, True))
        cursor.close()
        return cols
    
    def enum_columns(self, req, id):
        r"""Retrieve the columns present in a custom report.
        
        @param id     the report ID.
        @return       a list of tuples of the form 
                      (name, type, [label]).
        @throws       NotImplementedError if the report definition 
                      consists of saved custom query specified 
                      using a URL.
        @throws       QuerySyntaxError if the report definition 
                      consists of a TracQuery containing syntax errors.
        @throws       Exception in case of detecting any other error.
        """
        sql = self.get(req, id)['query']
        query = ''.join([line.strip() for line in sql.splitlines()])
        if query and (query[0] == '?' or query.startswith('query:?')):
          raise NotImplementedError('Saved custom queries specified ' \
                                  'using URLs are not supported.')
        elif query.startswith('query:'):
          query = Query.from_string(self.env, query[6:], report=id)
          fields = query.fields
          return [(f['name'], 'string', _(f['label'])) for f in fields] + \
                  [   ('changetime', 'number', _('Modified')), \
                      ('time', 'number', _('Created')), \
                      ('href', 'string', _('URL')), \
                      ('id', 'number', _('Ticket')), \
                  ]
        else:
          return self._sql_columns(req, id, sql)

#--------------------------------------------------
#   Version Control RPC
#--------------------------------------------------

def _normalize_timestamp(repos, req, timestamp, default=None):
  r"""Normalize datetime and revision numbers. Return only 
  datetime values.
  """
  if isinstance(timestamp, datetime):
    return timestamp
  elif isinstance(timestamp, xmlrpclib.DateTime):
    return rpc_to_datetime(timestamp, req)
  elif isinstance(default, (datetime, date, time)): # Return default
    return default
  else:
    return datetime.now(req.tz)

def _filter_revs(seq, repos, req, start, stop, full, \
                  accessor=None, log=None):
  r"""Filter values in seq so that only references to revisions 
  commited during a time interval be enumerated. 
  Items are binary tuples of the form `(revision id, changeset object)`.
  
  @param seq        original sequence to be filtered.
  @param repos      the repository managed by VCS.
  @param req        object containing information about the user 
                    requesting information in repository and more.
  @param start      boundary value. Revisions older than 
                    this value will not be retrieved. Dates 
                    and revision numbers are both accepted.
  @param stop       boundary value. Younger revisions 
                    will not be retrieved. Dates 
                    and revision numbers are both accepted.
  @param full       retrieve also the changeset object for revision.
  @param accesor    a function used to access the revision value 
                    stored in each item of the input sequence.
  @return           a sequence of tuples. The firts item is the 
                    element of the original sequence for which 
                    revision is in input time interval. The second is 
                    the changeset object or None (depending upon the 
                    value of `full` parameter)
  """
  if seq is not None:
    seq = iter(seq)
  if log is None:
    class VoidLogger:
      def __getattr__(self, attrnm):
        return lambda *args, **kwds: None
    log = VoidLogger()
  DO_NOTHING, DO_RETURN, DO_YIELD = xrange(3)
  load_chgset = True
  if isinstance(start, types.StringTypes) and \
      isinstance(stop, types.StringTypes):
    load_chgset = False
    if not repos.rev_older_than(stop, start):
      def cond(rev, chgset):
        if repos.rev_older_than(rev, start):
          return DO_RETURN
        elif repos.rev_older_than(stop, rev):
          return DO_NOTHING
        else:
          return DO_YIELD
    else:
      return                      # `start` committed after `stop`
  elif isinstance(start, types.StringTypes):
    if stop is None:
      load_chgset = False
      def cond(rev, chgset):
        # Process starts in youngest so there is no need to skip revisions
        return repos.rev_older_than(rev, start) and DO_RETURN or DO_YIELD
    else:
      ts = _normalize_timestamp(repos, req, stop)
      stop = repos.youngest_rev
      def cond(rev, chgset):
        if repos.rev_older_than(rev, start):
          return DO_RETURN
        else:
          if chgset.date < ts:
            return DO_YIELD
          else:
            return DO_NOTHING  
  elif isinstance(stop, types.StringTypes):
    if start is None:
      start = 0
      load_chgset = False
      def cond(rev, chgset):
        # Start in `stop` and stop in oldest so no need for DO_RETURN 
        # No need for DO_NOTHING since iterators will start from stop 
        # (assuming that revision numbers are valid and that's a 
        # precondition ;)
        return DO_YIELD
    else:
      ts = _normalize_timestamp(repos, req, start, _epoc)
      def cond(rev, chgset):
        # We start from `stop` so no need for DO_NOTHING ;)
        if chgset.date < ts:
            return DO_RETURN
        else:
          return DO_YIELD
  else:
    start_ts = _normalize_timestamp(repos, req, start, _epoc)
    stop_ts = _normalize_timestamp(repos, req, stop)
    start, stop = 0, repos.youngest_rev
    def cond(rev, chgset):
      ts = chgset.date
      if ts < start_ts:
          return DO_RETURN
      elif ts < stop_ts:
          return DO_YIELD
      else:
          return DO_NOTHING
  # Search backwards
  load_chgset = load_chgset or full
  try:
    while True:         # Stops when StopIteration is raised by seq
      item = seq.next()
      log.debug("IG: Processing item %s", item)
      if accessor:
        rev = accessor(item)
      else:
        rev = item
      log.debug("IG: Processing revision %s", rev)
      if repos.authz.has_permission_for_changeset(rev):
        try:
          chgset = load_chgset and repos.get_changeset(rev) or None
          action = cond(rev, chgset)
        except NoSuchChangeset:
          continue
        if action == DO_RETURN:
            return
        elif action == DO_YIELD:    # Implicit DO_NOTHING
          if full:
            yield item, chgset
          else:
            yield item, None
  except NoSuchChangeset:
    return

class VersionControlRPC(Component):
    r""" An interface to Trac's Repository and RepositoryManager.
    """ 
    implements(IXMLRPCHandler)

    # IXMLRPCHandler methods
    def xmlrpc_namespace(self):
        return 'source'
    
    def xmlrpc_methods(self):
        yield ('BROWSER_VIEW', 
                ((list, list, str, str, bool, int),
                 (list, list, str, str, bool), 
                 (list, list, str, str), 
                 (list, list, str), 
                 (list, list),), 
                 self.ls)
        yield ('BROWSER_VIEW', 
                ((list, list, str),
                 (list, list),), 
                 self.getFileAttributes)
        opt_types = [str, xmlrpclib.DateTime]
        yield ('CHANGESET_VIEW', 
                tuple(rpc_opt_sigs(list, None, opt_types, \
                                    opt_types, [bool])
                  ), 
                 self.getRevisions)
        yield ('CHANGESET_VIEW', 
                ((list, str, str, xmlrpclib.DateTime),
                 (list, str, str, str),
                 (list, str, str),
                 (list, str),), 
                 self.getFileHistory)
        yield ('CHANGESET_VIEW', 
                ((list, str),
                 (list, ),), 
                 self.enumChanges)
        yield ('CHANGESET_VIEW', 
                ((list, str),
                 (list, ),), 
                 self.normalize_rev)
                 
    # Exported methods
    def ls(self, req, files, filter_by=None, rev=None, rec=False, depth=None):
        r"""List information about the FILEs. The root path makes 
        reference to the top-level folder configured for the 
        repository according to some options in `trac.ini`. File path 
        separator is always `/`.
        
        @param files      target files and|or folders
        @param filter_by  a UNIX filename pattern used to filter the 
                          results.
        @param rev        target revision number. If missing (or 
                          negative) it defaults to HEAD (youngest).
        @param rec        list files contained in this folder and 
                          its subfolders recursively.
        @param depth      if recursive mode is on, specify the maximum
                          recursion level. In this case use `0` for 
                          files in the same folder (i.e. no recursion), 
                          `1` for files in folder and its immediate 
                          child entries, `2`, `3` ... and so on. If 
                          this value is negative then full recursion 
                          is performed.
        @return           a list containing the full name (i.e. 
                          relative to the root folder in VCS) of all 
                          the files inside the input folders. File 
                          names are not generated in order so files 
                          in a folder and its subfolders may appear 
                          in different positions. If the revision ID 
                          supplied in is invalid then an empty list 
                          is returned.
        """
        repos = RepositoryManager(self.env).get_repository(req.authname)
        if rev is None: rev = repos.youngest_rev
        if depth < 0: depth = None
        no_depth = depth is None
        already = set()
        
        for item in files:
          if isinstance(item, types.StringTypes):
            try:
              d, node = 0, repos.get_node(item, rev)
              path = item
            except NoSuchNode:
              continue
            except NoSuchChangeset:
              return
          else:
            d, node = item
            path = node.path
          if path not in already: # Dont process filename twice
            if node.isfile:
              if (not filter_by) or fnmatch(path, filter_by):
                yield path
            elif node.isdir:
              for child in node.get_entries():
                if (not filter_by) or fnmatch(child.path, filter_by):
                  yield child.path
                if child.isdir and rec and (no_depth or d < depth):
                  files.append([d + 1, child])
                elif child.isfile:
                  already.add(child.path)     # Mark filename
                else:
                  self.log.error("Unknown node type %s at %s", \
                                                node.kind, node.path)
            else:
              self.log.error("Unknown node type %s at %s", \
                                                node.kind, node.path)
            already.add(path)                 # Mark filename
    
    def getFileAttributes(self, req, files, rev=None):
        r"""Retrieve the attributes of a group of files. The root 
        path makes reference to the top-level folder configured for 
        the repository according to some options in `trac.ini`. File 
        path separator is always `/`.
        
        @param files      target files and|or folders
        @param rev        target revision number. If missing (or 
                          negative) it defaults to HEAD (youngest).
        @return           a list of dictionaries. Each one of them 
                          contains the attributes of the input file 
                          at that position. All data is calculated 
                          with respect to the target revision (see 
                          `rev` parameter). If the file does not 
                          exist or was created after commiting the 
                          target revision then `None` is returned 
                          instead. The following attributes are 
                          supported:
                          
                          - path :    filename (full path from root 
                                      folder)
                          - kind :    the type of node (e.g. one of 
                                        'file' or 'dir') at `path`.
                          - size :    file size in bytes
                          - ext  :    file extension
                          - mime :    MIME type if known
                          - changed : Modification date (date of `lastrev`)
                          - lastrev : Revision (prior to the target 
                                      revision) when the latest 
                                      modifications to this file were 
                                      commited
                          - log :     Commit message for last revision 
                                      (`chgrev`)
        """
        repos = RepositoryManager(self.env).get_repository(req.authname)
        if rev is None:
          rev = repos.youngest_rev
        mimeview = Mimeview(self.env)
        changesets = {}
        for path in files:
          try:
            node = repos.get_node(path, rev)
          except NoSuchNode:
            yield {}
            continue
          _rev = node.rev
          attrs = dict(path=node.path, kind=node.kind, lastrev=_rev)
          try:
            chgset = changesets[_rev]
            attrs.update(dict(changed=chgset.date, log=chgset.message))
          except KeyError:
            try:
              changesets[_rev] = chgset = repos.get_changeset(_rev)
              attrs.update(dict(changed=chgset.date, log=chgset.message))
            except NoSuchChangeset:
              changesets[_rev] = attrs['changed'] = attrs['log'] = None
          if node.isdir:
            attrs.update(dict(size=0, ext='', mime=''))
          elif node.isfile:
            # Copycat ! from trac.versioncontrol.web_ui.browser
            # MIME type detection 
            content = node.get_content()
            _chunk = content.read(CHUNK_SIZE)
            mime_type = node.content_type
            if not mime_type or mime_type == 'application/octet-stream':
                mime_type = mimeview.get_mimetype(node.name, _chunk) or \
                            mime_type or 'text/plain'
            
            attrs.update(size=node.get_content_length(), \
                          ext=splitext(node.path)[-1][1:], \
                          mime=mime_type)
          else:
            self.log.error("Unknown node type %s at %s", \
                                              node.kind, node.path)
          yield attrs
    
    REV_ATTRS = ['rev', 'message', 'author', 'date']
    
    def getRevisions(self, req, since=None, until=None, full=False):
        r"""Retrieve information about all revisions in a time 
        interval. Younger revisions should appear first.
        
        @param since      boundary value. Revisions older than 
                          this value will not be retrieved. Dates 
                          and revision numbers are both accepted.
        @param until      boundary value. Younger revisions 
                          will not be retrieved. Dates 
                          and revision numbers are both accepted.
        @param full       level of detail used to generate the data. 
                          If false only revision numbers 
                          are returned, else tuples of the form 
                          (rev, message, author, date) are returned 
                          for each changeset, where :
                          
                          - rev     : is the revision number (ID)
                          - message : commit message provided by 
                                      Version Control System
                          - author  : the user that committed changes 
                                      in this revision.
                          - date    : the date when this revision was 
                                      commited (as determined by VCS).
        @return           a list of data representing each 
                          revision in interval. The kind of 
                          information returned is controlled by `full` 
                          parameter.
                          
                          Note: Some revisions may be skipped if 
                          permissions state that the user performing 
                          the request has no access to that 
                          particular changeset.
        """
        repos = RepositoryManager(self.env).get_repository(req.authname)
        def iter_revs(lastrev):
          r"""Iterate over all revisions in repository.
          
          @param lastrev      start from this revision backwards. 
                              This value should be a normalized rev 
                              number
          @return             a list containing normalized rev numbers
          """
          rev = lastrev
          oldest_rev = repos.oldest_rev
          while rev != oldest_rev:
            yield rev
            rev = repos.normalize_rev(repos.previous_rev(rev))
          yield oldest_rev
        try:
          _rev = isinstance(until, types.StringTypes) and \
                              repos.normalize_rev(until) or \
                              repos.youngest_rev
          self.log.debug("IG: Stop at revision %r between [%r, %r]", \
                          _rev, repos.oldest_rev, repos.youngest_rev)
          seq = iter_revs(_rev)
        except NoSuchChangeset:
          return []
        else:
          seq = _filter_revs(seq, repos, req, since, until, full, \
                              log=self.log)
          if full:
            return (tuple(getattr(chg, a) for a in self.REV_ATTRS) \
                      for rev, chg in seq)
          else:
            return (rev for rev, chg in seq)
    
    def getFileHistory(self, req, path, rev=None, since=None):
        r"""Retrieve information about all the changes performed on a 
        file or directory in a time interval.
        
        @param path       file path in repository.
        @param since      boundary value. Revisions older than 
                          this value will not be retrieved. Dates 
                          and revision numbers are both accepted.
        @param rev        boundary value. Younger revisions 
                          will not be retrieved. Only revision 
                          numbers are allowed in this argument.
        @return           a list of `(path, rev, chg)` tuples, 
                          one for each revision in which the target 
                          was changed. This generator will follow 
                          copies and moves of a node (if the 
                          underlying version control system supports
                          that), which will be indicated by the 
                          first element of the tuple (i.e. the path) 
                          changing. Starts with an entry for the 
                          current revision.
                          
                          - path      : path the change was performed 
                                        upon
                          - rev       : revision number (ID)
                          - chg       : the kind of change being 
                                        performed. Supported values 
                                        are :
                            * add     : target was placed under 
                                        version control
                            * copy    : target was copied from 
                                        another location
                            * delete  : target was deleted
                            * edit    : target was modified
                            * move    : target was moved to 
                                        another location
                          
                          Note: Some revisions may be skipped if 
                          permissions state that the user performing 
                          the request has no access to that 
                          particular changeset.
        """
        if not isinstance(rev, (type(None), types.StringTypes)):
          raise ValueError("Revision ID must be a string")
        repos = RepositoryManager(self.env).get_repository(req.authname)
        try:
          node = repos.get_node(path, rev)
        except NoSuchNode:
          return []
        seq = node.get_history()
        seq = _filter_revs(seq, repos, req, since, rev, False, \
                            accessor=lambda x: x[1], log=self.log)
        return (x[0] for x in seq)
    
    def enumChanges(self, req, rev=None):
        r"""Enumerate all the changes performed at a given revision.
        
        @param rev        The ID of the target revision (changeset). 
                          Only numbers are allowed in this argument.
        @return           A list of tuples describing every change in 
                          the changeset. The tuple will contain 
                          `(path, kind, change, base_path, base_rev)`,
                          where :
                          
                          - change    : the kind of change being 
                                        performed (for further details 
                                        read the docstrings of 
                                        `getFileHistory` method).
                          - kind      : the type of node (e.g. one of 
                                        'file' or 'dir') at `path`.
                          - path      : is the targeted path for the 
                                        `change` (which is the 
                                        ''deleted'' path  for a 
                                        DELETE change).
                          - base_path : the source path for the
                                        action (empty string  in the 
                                        case of an ADD change).
                          - base_rev  : the source rev for the
                                        action (empty string in the 
                                        case of an ADD change).
                          
                          Note: Some revisions may be skipped if 
                          permissions state that the user performing 
                          the request has no access to that 
                          particular changeset.
        """
        repos = RepositoryManager(self.env).get_repository(req.authname)
        if rev is None:
          rev = repos.youngest_rev
        try:
          chgset = repos.get_changeset(rev)
        except NoSuchChangeset:
          return []
        return ((p, k, chg, bp or '', brev or '') \
                      for p, k, chg, bp, brev in chgset.get_changes())
    
    def normalize_rev(self, req, rev=None):
        r"""Return a canonical representation of a revision.

        It's up to the backend to decide which string values of `rev` 
        (usually provided by the user) should be accepted, and how they 
        should be normalized. Some backends may for instance want to 
        match against known tags or branch names.
        
        In addition, if `rev` is missing or '', the youngest revision 
        should be returned.
        
        @param rev        The ID of the target revision (changeset).
        @return           A list of tuples describing every change in 
                          the changeset. The tuple will contain 
        """
        repos = RepositoryManager(self.env).get_repository(req.authname)
        return repos.normalize_rev(rev)
