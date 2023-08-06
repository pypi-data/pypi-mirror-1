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

r"""Data sources used to publish the data about files managed by the 
Version Control System (e.g. `svn`) used by Trac. This includes 
revisions, change log, and (source) files.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

from api import gviz_col, gviz_param, GVizBadRequestError
from util import GVizXMLRPCAdapter, convert_req_date, \
                  REQFIELDS_DESC, REQFIELDS_DEFAULTS

import types

#--------------------------------------------------
# Source files
#--------------------------------------------------

class GVizSourceBase(GVizXMLRPCAdapter):
  abstract = True
  
  FA_CODE = compile('(path, kind, size, ext, mime, changed, lastrev)', \
                            '<string>', 'eval')
  
  def _normalize_rev(self, rev, req, fmt=REQFIELDS_DEFAULTS['datefmt']):
    r"""Converts a value in a client request making reference to a 
    revision committed to the source repository.
    
    @param rev          the value received in the HTTP request.
    @param fmt          datetime format used to convert string (not 
                        needed if allow_date is false).
    @param req          request object (not needed if allow_date is 
                        false, mandatory otherwise).
    """
    try:
      return convert_req_date(rev, fmt, req, False)
    except GVizBadRequestError:
      return rev
  
  def _requested_files(self, req, files, filter=None, rev=None, \
                        rec=False, depth=None):
    if isinstance(files, types.StringTypes):
      files = [files]
    if depth is not None:
      try:
        depth = int(depth)
      except ValueError:
        raise GVizBadRequestError("Recursion depth must be an integer value")
    return self._rpc_obj.ls(req, files, filter, rev, rec, depth)
    
  def xmlrpc_namespace(self):
      r"""Use Version Control XML-RPC.
      """
      return ('source',)

class GVizSourceFiles(GVizSourceBase):
    r"""Return information about the files managed by the Version 
    Control System (e.g. `svn`) connected to the Trac environment.
    
    This component depends on tracgviz.rpc.VersionControlRPC. The 
    later must be enabled. Please read 
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    
    # IGVizDataProvider methods
    def get_data_schema(self, req):
        r"""Return file attributes.
        """
        return [('path', 'string'), ('kind', 'string'), \
                ('size', 'number'), \
                ('ext', 'string'), ('mime', 'string'), \
                ('changed', 'datetime'), ('lastrev', 'string'),
                ('log', 'string'), ]
    
    @gviz_param('file',     "target files and|or folders. Can be "
                              "specified more than once in order to "
                              "process multiple files.")
    @gviz_param('filter', "a UNIX filename pattern used to filter "
                      "the results.")
    @gviz_param('rev',       "target revision number. If missing (or "
                      "negative) it defaults to HEAD (youngest).")
    @gviz_param('rec',       "list files contained in this folder and "
                      "its subfolders recursively.")
    @gviz_param('depth',     "if recursive mode is on, specify the "
                      "maximum recursion level. In this case use `0` "
                      "for files in the same folder (i.e. no recursion), "
                      "`1` for files in folder and its immediate "
                      "child entries, `2`, `3` ... and so on. If "
                      "this value is negative then full recursion "
                      "is performed.")
    @gviz_col('path',    "filename (full path from root "
                          "folder)")
    @gviz_col('kind',     "the type of node (e.g. one of "
                          "'file' or 'dir') at `path`.")
    @gviz_col('size',    "file size in bytes")
    @gviz_col('ext', "    file extension")
    @gviz_col('mime',    "MIME type if known")
    @gviz_col('changed', "Modification date (date of `lastrev`)")
    @gviz_col('lastrev', "Revision (prior to the target "
                          "revision) when the latest "
                          "modifications to this file were "
                          "commited")
    @gviz_col('log',     "Commit message for last revision "
                          "(`lastrev`)")
    def get_data(self, req, tq, file='/', filter=None, rev=None, \
                        rec=False, depth=None, **tqx):
        r"""Retrieve files attributes.
        """
        files = self._requested_files(req, file, filter, rev, rec, \
                                        depth)
        if rec is not False:
          rec = True
        revs = dict()
        
        fa_meth = self._rpc_obj.getFileAttributes
        ra_meth = self._rpc_obj.getRevisions
        return (eval(self.FA_CODE, attrs) + \
                    (revs.setdefault(attrs['lastrev'], \
                                      iter(ra_meth(req, \
                                              str(attrs['lastrev']), \
                                              str(attrs['lastrev']), \
                                              True)).next()[1]),) \
                    for attrs in fa_meth(req, files, rev) if attrs)
    
    def gviz_namespace(self):
        return ('source', 'files')

class GVizSourceFileHistory(GVizSourceBase):
    r"""Return information about the historical events recorded by 
    Version Control System (e.g. `svn`) leading to the presence 
    of a group of files in a given revision.
    
    This component depends on tracgviz.rpc.VersionControlRPC. The 
    later must be enabled. Please read 
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    
    # IGVizDataProvider methods
    def get_data_schema(self, req):
        r"""Return event fields.
        """
        return [('path', 'string'), ('target', 'string'), \
                ('rev', 'string'), ('chg', 'string'),
                ('kind', 'string'), ('size', 'number'), \
                ('ext', 'string'), ('mime', 'string'), \
                ('changed', 'datetime'), ('log', 'string'), 
                ]
    
    @gviz_param('file',     "target files and|or folders. Can be "
                              "specified more than once in order to "
                              "process multiple files.")
    @gviz_param('filter', "a UNIX filename pattern used to filter "
                      "the results.")
    @gviz_param('rev',       "target revision number. If missing (or "
                      "negative) it defaults to HEAD (youngest).")
    @gviz_param('rec',       "list files contained in this folder and "
                      "its subfolders recursively.")
    @gviz_param('depth',     "if recursive mode is on, specify the "
                      "maximum recursion level. In this case use `0` "
                      "for files in the same folder (i.e. no recursion), "
                      "`1` for files in folder and its immediate "
                      "child entries, `2`, `3` ... and so on. If "
                      "this value is negative then full recursion "
                      "is performed.")
    @gviz_param('since',     "boundary value. Revisions older than "
                          "this value will not be retrieved. Dates "
                          "and revision numbers are both accepted.")
    @gviz_param('fmt', REQFIELDS_DESC['datefmt'] % \
                            dict(args='`since`', plural=''))
    @gviz_col('path',     "this field makes reference to the original "
                          "path of the file whose changes have "
                          "been requested.")
    @gviz_col('target',   "path to the file upon which the change "
                          "was performed.")
    @gviz_col('rev',      "revision number (ID).")
    @gviz_col('chg',      "the kind of change being "
                          "performed. Supported values "
                          "are :"
                          "  * add     : target was placed under "
                                      "version control"
                          "  * copy    : target was copied from "
                                      "another location"
                          "  * delete  : target was deleted"
                          "  * edit    : target was modified"
                          "  * move    : target was moved to "
                                      "another location")
    @gviz_col('kind',     "the type of node (e.g. one of "
                          "'file' or 'dir') at `target`.")
    @gviz_col('size',    "size of `target` in bytes")
    @gviz_col('ext',     "extension of `target`")
    @gviz_col('mime',    "MIME type of `target` if known")
    @gviz_col('changed', "Modification date of `target` (date of `rev`)")
    @gviz_col('log',     "Commit message for last revision "
                          "(`lastrev`)")
    def get_data(self, req, tq, file='/', filter=None, rev=None, \
                        rec=False, depth=None, since=None, \
                        fmt=REQFIELDS_DEFAULTS['datefmt'], **tqx):
        r"""Retrieve changes in file history.
        """
        files = self._requested_files(req, file, filter, rev, rec, \
                                        depth)
        if since is not None:
          since = self._normalize_rev(since, req, fmt)
        fh_meth = self._rpc_obj.getFileHistory
        fa_meth = self._rpc_obj.getFileAttributes
        ra_meth = self._rpc_obj.getRevisions
        revs = dict()
        def_attrs = {'size' : None, 'mime' : None, 'changed' : None,
                      'kind' : None, 'last_rev': None}
        for path in files:
          for target, _rev, chg in fh_meth(req, path, rev, since):
            attrs = fa_meth(req, [target], _rev)[0] or \
                    def_attrs.copy().update(dict(path=target, \
                                          ext=splitext(target)[-1][1:]))
            yield (path, target, _rev, chg) + \
                    eval(self.FA_CODE, attrs)[1:-1] + \
                    (revs.setdefault(_rev, \
                                      iter(ra_meth(req, str(_rev), 
                                            str(_rev), True)).next()[1]),)
    
    def gviz_namespace(self):
        return ('source', 'file', 'history')

#--------------------------------------------------
# Chagesets
#--------------------------------------------------

class GVizChangesetDetails(GVizSourceBase):
    r"""Return a set of changes committed at once in a repository.
    
    This component depends on tracgviz.rpc.VersionControlRPC. The 
    later must be enabled. Please read 
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    
    # IGVizDataProvider methods
    def get_data_schema(self, req):
        r"""Return event fields.
        """
        return [('rev', 'string'), ('chg', 'string'), \
                ('kind', 'string'), ('target', 'string'), \
                ('base_path', 'string'), ('base_rev', 'string') \
                ]
    
    @gviz_param('rev',       "target revision number. If missing (or "
                      "negative) it defaults to HEAD (youngest). "
                      "This parameter can be specified more than once "
                      "in order to retrieve changes committed in "
                      "multiple revisions.")
    @gviz_param('since',    "used to select revisions in an interval. "
                            "Works together with `until` parameter, "
                            "but nothing happens if both are missing. "
                            "Revisions younger than "
                            "this value and older than `until` will "
                            "be processed too. Dates "
                            "and revision numbers are both accepted.")
    @gviz_param('until',    "used to select revisions in an interval. "
                            "Works together with `since` parameter, "
                            "but nothing happens if both are missing. "
                            "Revisions older than "
                            "this value and younger than `since` will "
                            "be processed too. Dates "
                            "and revision numbers are both accepted.")
    @gviz_param('fmt', REQFIELDS_DESC['datefmt'] % \
                            dict(args='both `since` and `until`', \
                                  plural='s'))
    @gviz_col('rev',      "revision number (ID).")
    @gviz_col('chg',      "the kind of change being "
                          "performed. Supported values "
                          "are :"
                          "  * add     : target was placed under "
                                      "version control\n"
                          "  * copy    : target was copied from "
                                      "another location\n"
                          "  * delete  : target was deleted\n"
                          "  * edit    : target was modified\n"
                          "  * move    : target was moved to "
                                      "another location")
    @gviz_col('kind',     "the type of node (e.g. one of "
                          "'file' or 'dir') at `path`.")
    @gviz_col('target',   "path to the file involved in the change.")
    @gviz_col('base_path',"the source path for the"
                          "action (`None` in the case of "
                          "an ADD change).")
    @gviz_col('base_rev', "the source rev for the"
                          "action (`-1` in the case of "
                          "an ADD change).")
    def get_data(self, req, tq, rev=None, since=None, until=None, 
                                fmt=REQFIELDS_DESC['datefmt'], **tqx):
        r"""Retrieve changes in revision.
        """
        rpc_obj = self._rpc_obj
        already = set()
        if not isinstance(rev, list):
          rev = (rev,)
        for r in rev:
          try:
            r = rpc_obj.normalize_rev(req, r)
          except:
            raise
          if r not in already:
            for chg in rpc_obj.enumChanges(req, r):
              yield (r,) + chg
            already.add(r)       # Mark revision
        if (since, until) != (None, None):
          if since is not None:
            since = self._normalize_rev(since, req, fmt)
          if until is not None:
            until = self._normalize_rev(until, req, fmt)
          for r in rpc_obj.getRevisions(req, since, until):
            if r not in already:
              for chg in rpc_obj.enumChanges(req, r):
                yield (r,) + chg
    
    def gviz_namespace(self):
        return ('source', 'changes')

class GVizChangesets(GVizSourceBase):
    r"""Return meta-data about all the revisions commited to the 
    repository.
    
    This component depends on tracgviz.rpc.VersionControlRPC. The 
    later must be enabled. Please read 
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    
    # IGVizDataProvider methods
    def get_data_schema(self, req):
        r"""Return fields in revision log.
        """
        return [('rev', 'string'), ('message', 'string'), \
                 ('author', 'string'), ('date', 'datetime')]
    
    @gviz_param('since',    "boundary value. Revisions older than "
                            "this value will not be retrieved. Dates "
                            "and revision numbers are both accepted.")
    @gviz_param('until',    "boundary value. Younger revisions "
                            "will not be retrieved. Dates "
                            "and revision numbers are both accepted.")
    @gviz_param('fmt', REQFIELDS_DESC['datefmt'] % \
                            dict(args='both `since` and `until`', \
                                  plural='s'))
    @gviz_col('rev',        "is the revision number (ID)")
    @gviz_col('message',    "commit message provided by "
                            "Version Control System")
    @gviz_col('author',     "the user that committed changes "
                            "in this revision.")
    @gviz_col('date',       "the moment when this revision was "
                            "commited (as determined by VCS).")
    def get_data(self, req, tq, since=None, until=None, 
                        fmt=REQFIELDS_DEFAULTS['datefmt'], **tqx):
        r"""Retrieve revision log.
        """
        if since is not None:
          since = self._normalize_rev(since, req, fmt)
        if until is not None:
          until = self._normalize_rev(until, req, fmt)
        obj = self._rpc_obj.getRevisions(req, since, until, True)
        self.log.debug("IG: RPC result %s ", obj)
        return obj
    
    def gviz_namespace(self):
        return ('source', 'revlog')


