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

"""This module contains every WikiFirmatting extension being related 
to Trac GViz system.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

__all__ = 'GVizProviderListMacro', 'GoogleDocsConnector', \
            'GoogleVizGadgets', 'GoogleAppsConnector', \
            'LinksTreeDispatcher', 'GVizWikiPages'

from trac.core import Interface, Component, ExtensionPoint, \
        implements, TracError
from trac.attachment import Attachment
from trac.config import Option
from trac.mimeview.api import Context
from trac.util import get_pkginfo
from trac.web.api import IRequestHandler, RequestDone
from trac.web.href import Href
from pkg_resources import resource_string, resource_filename
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor
from trac.web.api import IRequestHandler
from trac.web.chrome import ITemplateProvider, add_stylesheet
from trac.wiki.api import IWikiSyntaxProvider, parse_args
from trac.wiki.macros import WikiMacroBase
from trac.wiki.formatter import Formatter, system_message

from genshi.core import Markup
from genshi.builder import tag, Element
from genshi.template import MarkupTemplate

from cgi import parse_qs
from fnmatch import fnmatch
from inspect import getargspec
from itertools import chain, izip, repeat
from os.path import join, exists
from os import makedirs
from re import compile
import types
from urlparse import urlunparse
from urllib import urlencode
from xmlrpclib import DateTime

from api import TracGVizSystem, gviz_api, ITracLinksHandler, \
                GVizBadRequest, gviz_col, gviz_param
from util import GVizXMLRPCAdapter, convert_req_date

__metaclass__ = type

#--------------------------------
# Wiki formatting
#--------------------------------

class LinksTreeDispatcher(Component):
    """A class used to dispatch TracLinks resolution requests to the 
    providers registered under the `gadget` namespace.
    """
    implements(IWikiSyntaxProvider)
    resolvers = ExtensionPoint(ITracLinksHandler)
    
    # IWikiSyntaxProvider methods
    def get_wiki_syntax(self):
        """No further syntax.
        """
        return []
    
    def _format_link(self, formatter, ns, target, label):
        parts = tuple(target.split(':'))
        self.log.debug('IG: Processing TracLinks expression %s', target)
        for _ns, f in ([_ns, f] for x in self.resolvers \
                        for _ns, f in x.get_link_resolvers() \
                        if ns == _ns[0]):
            self.log.debug('IG: Matching namespace %s', _ns)
            _ns = _ns[1:]
            if all(x == y for x, y in zip(parts, _ns)) and \
                    len(parts) >= len(_ns):
                target = ':'.join(parts[len(_ns):])
                break;
        else:
            return tag.a(label, class_='missing attachment', rel='nofollow')
        return f(formatter, _ns, target, label)
        
    def get_link_resolvers(self):
        """Return an iterable over (namespace, formatter) tuples.

        Each formatter should be a function of the form
        fmt(formatter, ns, target, label), and should
        return some HTML fragment.
        The `label` is already HTML escaped, whereas the `target` is not.
        """
        yield ('gadget', self._format_link)
        yield ('gviz', self._format_link)

class GVizProviderListMacro(WikiMacroBase):
    """Displays a list of all installed GViz data providers, 
    including documentation if available. 
    
    Optionally, the namespace of a specific provider can be provided 
    as an argument. In that case, only the documentation for that 
    data source will be rendered. 
    
    Note that this macro will not be able to display the 
    documentation if the `PythonOptimize` option is enabled 
    for mod_python!.
    
    Important: The function assumes that the signatures of `get_data`
                methods dont contain nested args. If this is the 
                case the results are unpredictable.
    """
    
    ERR_MSG = "<strong>Unable to retrieve documentation " \
            "for '%(ns)s'. %(reason)s </strong>"
    PROVIDER_DOC = r"""
        <html xmlns="http://www.w3.org/1999/xhtml"
              xmlns:py="http://genshi.edgewall.org/">
          <?python
          from itertools import count
          idx = count()
          ?>
          <py:def function="attr_desc(name, value)">
            <tr class="${idx.next() % 2 and 'odd' or None}">
              <th scope="row"><var>$name</var></th>
              <td colspan="4"><small>$value</small></td>
            </tr>
          </py:def>
          <br/>
          <strong> GViz data provider: ${p.__class__.__name__}</strong>
          <br/>
          <table class="listing">
            <thead>
              <tr>
                <th>Property</th>
                <th colspan="4">Value</th>
              </tr>
            </thead>
            <tbody>
              ${attr_desc('Name', p.__class__.__name__)}
              ${attr_desc('Module', p.__class__.__module__)}
              ${attr_desc('Namespace', '.'.join(p.gviz_namespace()))}
              ${attr_desc('Relative URL', '/gviz/' + \
                                '/'.join(p.gviz_namespace()))}
              ${attr_desc('Description', p.__doc__)}
            </tbody>
            <thead>
              <tr>
                <th colspan="5">Columns</th>
              </tr>
              <tr>
                <th>Index</th>
                <th>ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr py:for="idx, col in enumerate(cols)" class="${idx % 2 and 'odd' or None}">
                <td>$idx</td>
                <td><nobr>${col['id']}</nobr></td>
                <td>${col['label']}</td>
                <td>${col['type']}</td>
                <td>${docs.get(col['id'], '(None)')}</td>
              </tr>
            </tbody>
            <thead>
              <tr>
                <th colspan="5">Parameters</th>
              </tr>
              <tr>
                <th>Name</th>
                <th>Default value</th>
                <th colspan="3">Description</th>
              </tr>
            </thead>
            <tbody>
              <tr py:for="idx, (nm, desc, defv) in enumerate(pdocs)" 
                    class="${idx % 2 and 'odd' or None}">
                <td><nobr>$nm</nobr></td>
                <td>$defv</td>
                <td colspan="3">$desc</td>
              </tr>
            </tbody>
          </table>
        </html>
    """
    
    def _provider_doc(self, provider):
        try:
            cols = gviz_api.DataTable.TableDescriptionParser( \
                        provider.get_data_schema())
            tmpl = MarkupTemplate(self.PROVIDER_DOC)
            try:
                anns = provider.get_data.func_annotations
            except AttributeError:
                anns = docs = dict()
            else:
                docs = anns.get('return', dict())
                args, _, varkw, defs = getargspec(provider.get_data)
                pdocs = ([nm, anns.get(nm), defv] \
                            for nm, defv in izip( \
                                  reversed(args[3:]), \
                                  chain(reversed(defs or []), \
                                           repeat(None))))
                if varkw is not None:
                    pdocs = chain(pdocs, [['Further key/value pairs', 
                                    anns.get(varkw, 'Ignored'),
                                    'None']])
            stream = tmpl.generate(cols=cols, p=provider, docs=docs, \
                                    pdocs= pdocs)
            return stream.render('xhtml')
        except Exception, exc:
            self.log.exception("IG: Generating provider docs ... failed")
            return str(system_message('Could not generate docs for %s' \
                                        '. Error message: %s' % \
                                        (provider.__class__.__name__,
                                            str(exc))))
    
    def expand_macro(self, formatter, name, ns):
        self.log.debug('IG: GVizProviderListMacro -> ns = %s', ns)
        ERR_MSG = self.ERR_MSG
        try:
            gvizsys = TracGVizSystem(self.env)
        except:
            return Markup(ERR_MSG % dict(ns=ns, reason='Please enable '
                            'TracGVizSystem in trac.ini'))
        else:
            if ns:
                try:
                    providers = [gvizsys._cache['/gviz/' + ns]]
                except KeyError:
                    return Markup(ERR_MSG % dict(ns=ns, reason='Provider '
                                    'not found'))
            else:
                providers = gvizsys._cache.itervalues()
            doc = reduce(lambda acc, x: acc + x, \
                         (self._provider_doc(p) for p in providers), \
                         '')
            return Markup(doc)

#-------------------------------------
#   WikiFormatting & Google services
#-------------------------------------

class GoogleDocsConnector(Component):
    r"""Provide shortcuts to the features found in Google Spreadsheets 
    being related to Google Visualization API.
    
    Syntax -> 
    gviz:google:sheet:<spreadsheet_id>[:[<sheet_name>][:<top_cell>-<bottom_cell>]][?[headers=<number>]]
    
    Example(s) ->
    - gviz:google:sheet:12345::B12-U37?headers=1
      http://spreadsheets.google.com/tq?headers=1&range=B12%3AU37&key=12345
    - gviz:google:sheet:12345:Sheet1:B12-U37?headers=1
      http://spreadsheets.google.com/tq?headers=1&range=B12%3AU37&key=12345&sheet=Sheet1
    - gviz:"google:sheet:12345:Sheet 1"
      http://spreadsheets.google.com/tq?sheet=Sheet+1&key=12345
    - gviz:"google:sheet:12345:Sheet 1:B12-U37?headers=1"
      http://spreadsheets.google.com/tq?sheet=Sheet+1&key=12345&headers=1&range=B12%3AU37
    """
    implements(ITracLinksHandler)
    
    RE_SHEET_INFO = compile(r'^(?P<key>(?:\w|[-])+)'
                            '(?:[:]'
                              '(?P<sheet>(?:\w|\s)+)?'
                              '(?:[:](?P<tl>[A-Z]\d+)[-](?P<br>[A-Z]\d+))?'
                            ')?$'
                            )
    
    # ITracLinksHandler methods
    def _format_link(self, formatter, ns, sheet_info, label):
        path, query, fragment = formatter.split_link(sheet_info)
#        try:
#            id, range = path.rsplit(':', 1)
#            start, end = range.split('-')
#            range = start + ':' + end
#        except ValueError:
#            id = path
#            range = None
        mo = self.RE_SHEET_INFO.match(path)
        if mo is None:
          raise TracError('Invalid spreadsheet info : %s' % (sheet_info,))
        args = mo.groupdict()
        start = args.pop('tl')
        end = args.pop('br')
        
        try:
          _range = start + ':' + end
        except:
          _range = None
        self.log.debug('IG: Spreadsheet parameters %s', query)
        try:
            query = query[1:]
        except ValueError:
            headers = None
        else:
            headers = parse_qs(query).get('headers')
        
        title = "Google spreadsheet # %s " % (args.get('key'),)
        sheet_nm = args.get('sheet')
        if sheet_nm is not None:
          sheet_nm = '(in sheet %s)' % (sheet_nm,)
        else:
          sheet_nm = '(default sheet)'
        title+= sheet_nm
        if _range is not None:
            title+= " (in range %s)" % (start + '-' + end,)
        if not label:
            label = title
        url = Href('http://spreadsheets.google.com/tq')
        url = url(range=_range, headers=headers, **args)

        return formatter._make_ext_link(url, label, title)
    
    def get_link_resolvers(self):
        """Return an iterable over (namespace, formatter) tuples.

        Each formatter should be a function of the form
        fmt(formatter, ns, target, label), and should
        return some HTML fragment.
        The `label` is already HTML escaped, whereas the `target` is not.
        """
        yield (('gviz', 'google', 'sheet'), self._format_link)

class GoogleVizGadgets(Component):
    """Provide shortcuts based on WikiFormatting so as to specify 
    URLs for (standard) Google Visualization Gadgets.
    
    Syntax -> 
    gadget:google:modules:<chart_name>
    
    Example(s) ->
    - gadget:google:modules:line-chart
      http://www.google.com/ig/modules/line-chart.xml
    """
    implements(ITracLinksHandler)
    
    # ITracLinksHandler methods
    def _format_link(self, formatter, ns, viz_name, label):
        title = "Google's Official Visualization: %s" % (viz_name,)
        url = 'http://www.google.com/ig/modules/%s.xml' % (viz_name,)
        return formatter._make_ext_link(url, label, title)
    
    def get_link_resolvers(self):
        """Return an iterable over (namespace, formatter) tuples.

        Each formatter should be a function of the form
        fmt(formatter, ns, target, label), and should
        return some HTML fragment.
        The `label` is already HTML escaped, whereas the `target` is not.
        """
        yield (('gadget', 'google', 'modules'), self._format_link)

class GoogleAppsConnector(Component):
    """Provide shortcuts to the visualization URL for specific 
    data sources defined for your domain and made available via Google 
    Apps Visualization API.
    
    Syntax -> 
    gviz:google:apps:<report_key>@<report_date>:<domain>[?tq=<query>]
    
    Example(s) ->
    - gviz:"google:apps:asdfa014mm129anpsmdasdas123@2008-08-31:example.com?tq=select rdate,count_7_day_actives where count_7_day_actives > 100"
      https://www.google.com/a/cpanel/example.com/ReportGviz?reportDate=2008-08-31&reportKey=asdfa014mm129anpsmdasdas123&tq=select+rdate%2Ccount_7_day_actives+where+count_7_day_actives+%3E+100
    """
    implements(ITracLinksHandler)
    
    PATH_LINK_RE = compile(r"([^@:]+)"     # report id
                              r"@(\d\d\d\d-\d\d-\d\d)" # report date
                              r":(.+)$" # domain
                              )
    
    # ITracLinksHandler methods
    def _format_link(self, formatter, ns, report_info, label):
        path, query, fragment = formatter.split_link(report_info)
        match = self.PATH_LINK_RE.match(path)
        if match:
            report, date, domain = match.groups()
        else:
            raise TracError("Invalid syntax or missing fields in %s ." \
                            "Syntax -> gviz:google:apps:<report_key>" \
                            "@<report_date>:<domain>[?tq=<query>]" % \
                                (report_info,))
        try:
            query = query[1:]
        except ValueError:
            pass
        else:
            query = parse_qs(query).get('tq')
        
        title = "Google Apps Report # %s at %s for domain %s" % \
                    (report, date, domain)
        if query is not None:
            title+= " (with query)"
        if not label:
            label = title
        url = Href('https://www.google.com/a/cpanel/')
        url = url(domain, 'ReportGviz', reportKey=report, 
                    reportDate=date, tq=query)
        return formatter._make_ext_link(url, label, title)
    
    def get_link_resolvers(self):
        """Return an iterable over (namespace, formatter) tuples.

        Each formatter should be a function of the form
        fmt(formatter, ns, target, label), and should
        return some HTML fragment.
        The `label` is already HTML escaped, whereas the `target` is not.
        """
        yield (('gviz', 'google', 'apps'), self._format_link)

#--------------------------------
# Data sources
#--------------------------------

class BaseWikiResultSet(GVizXMLRPCAdapter):
    abstract = True
    def _retrieve_pages(self, req, ids=None, since=None):
        r"""Parse the page names supplied in to `ids` parameter. If none 
        is specified then return all the pages modified since a 
        given timestamp or, if missing, return the names of all pages.
        """
        if ids is not None:
            all_wikis = []
            def wiki_expand(wikifn):
              if any(wildchar in wikifn for wildchar in '*?['):
                if not all_wikis:
                  all_wikis.append(self._rpc_obj.getAllPages(req))
                return (pageid for pageid in all_wikis[0] \
                                if fnmatch(pageid, wikifn))
              else:
                return (wikifn,)
            
            if isinstance(ids, types.StringTypes):
                ids = (ids,)
            else:
                ids = dict([x, None] for x in ids).iterkeys()
            
            return dict([pageid, None] \
                        for wikifn in ids \
                        for pageid in wiki_expand(wikifn)).iterkeys()
        elif since is not None:
            return (x['name'] for x in self._rpc_obj.getRecentChanges(req, since))
        else:
            return self._rpc_obj.getAllPages(req)
    
    def xmlrpc_namespace(self):
        """Use Wiki XML-RPC."""
        return ('wiki',)
    
class GVizWikiPages(BaseWikiResultSet):
    """Returns information about the different versions of the wiki 
    pages created in the site.
    
    This component depends on tracrpc.ticket.WikiRPC. The later 
    must be enabled. Please read 
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    # IGVizDataProvider methods
    def get_data_schema(self):
        return {'name' : 'string', 'version' : 'number', \
                'lastModified' : 'datetime', 'author' : 'string', \
                'comment' : 'string'
                }
    
    @gviz_col('name', "The wiki page name.")
    @gviz_col('version', "All the other information is related to "
                            "this version of the wiki page.")
    @gviz_col('lastModified', "The date when this page (version) was created.")
    @gviz_col('author', "The user that was performing this change.")
    @gviz_col('comment', "Brief description about the change being made.")
    @gviz_param('all', "Retrieve *ALL* the versions matching the "
                        "specified criteria. If missing, consider only "
                        "the latest version of each page.")
    @gviz_param('since', "Retrieve only the pages modified since "
                            "timestamp (UTC). Should be specified "
                            "only once.")
    @gviz_param('name', "Selects specific pages. May be specified "
                            "more than once in order to retrieve "
                            "information about multiple pages.")
    @gviz_param('fmt', "The syntax of `since` field. Here you "
                            "can embed the directives supported by "
                            "`time.strftime` function. The default "
                            "behavior is to accept the well known "
                            "format `yyyy-mm-dd HH:MM:SS` which is "
                            "actually written like this "
                            "`%Y-%m-%d %H:%M:%S`.")
    def get_data(self, req, tq, name=None, all=None, since=None, \
                    fmt="%Y-%m-%d %H:%M:%S", **tqx):
        """Retrieve information about wiki pages.
        """
        obj = self._rpc_obj
        try:
            if since is not None:
                since = convert_req_date(since, fmt, req)
        except:
            raise GVizBadRequest('Invalid date time value %s' % (since,))
        pages = self._retrieve_pages(req, name, since)
        for page in pages:
            info = obj.getPageInfo(req, page)
            if since is None or info['lastModified'] >= since:
                yield info
            if all is not None:
                for version in xrange(info['version'] - 1, 0, -1):
                    info = obj.getPageInfo(req, page, version)
                    if info:
                        if since is not None and \
                                info['lastModified'] < since:
                            break
                        yield info
    
    def gviz_namespace(self):
        return ('wiki', 'index')

class GVizWikiAttachments(BaseWikiResultSet):
    """Returns information about the different files attached to wiki 
    pages.
    
    This component depends on tracrpc.ticket.WikiRPC. The later 
    must be enabled. Please read 
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    # IGVizDataProvider methods
    def get_data_schema(self):
        return [('owner', 'string'), ('path', 'string'), \
                ('filename', 'string'), ('size', 'number'), \
                ('date', 'datetime'), ('author', 'string'), \
                ('description', 'string'), ('url', 'string')
                ]
    
    @gviz_col('owner', "The name of the wiki page containing the "
                        "attachment.")
    @gviz_col('path', "The path identifying the attachment.")
    @gviz_col('filename', "The attached file name.")
    @gviz_col('url', "The URL to download the file.")
    @gviz_col('size', "The attached file size.")
    @gviz_col('date', "The moment when this file was uploaded.")
    @gviz_col('author', "The agent (user) that uploaded the file.")
    @gviz_col('description', "Brief comment about the contents of the "
                            "file.")
    @gviz_param('all', "Retrieve *ALL* the attachments in these pages "
                        "disregarding the time when they were uploaded. "
                        "If missing only those attachments uploaded "
                        "after the date supplied in `since` argument "
                        "will be retrieved.")
    @gviz_param('since', "Retrieve only those attachments found "
                            "in pages modified since "
                            "timestamp (UTC). Should be specified "
                            "only once.")
    @gviz_param('name', "Selects specific pages. May be specified "
                            "more than once in order to retrieve "
                            "information about multiple pages.")
    @gviz_param('fmt', "The syntax of `since` field. Here you "
                            "can embed the directives supported by "
                            "`time.strftime` function. The default "
                            "behavior is to accept the well known "
                            "format `yyyy-mm-dd HH:MM:SS` which is "
                            "actually written like this "
                            "`%Y-%m-%d %H:%M:%S`.")
    def get_data(self, req, tq, name=None, all=None, since=None, \
                    fmt="%Y-%m-%d %H:%M:%S", **tqx):
        """Retrieve information about attachments in wiki pages.
        """
        obj = self._rpc_obj
        try:
            if since is not None:
                _since = convert_req_date(since, fmt, req, False)
                since = DateTime(_since)
        except:
            raise GVizBadRequest('Invalid date time value %s' % (since,))
        pages = self._retrieve_pages(req, name, since)
        for page in pages:
            for path in obj.listAttachments(req, page):
                page, fnm = path.rsplit('/', 1)
                resobj = Attachment(self.env, 'wiki', page, fnm)
                if all is not None or since is None or \
                        resobj.date >= _since:
                    yield (page, path, resobj.filename, resobj.size, \
                            resobj.date, resobj.author, \
                            resobj.description, 
                            req.abs_href('attachment/wiki', path))
    
    def gviz_namespace(self):
        return ('wiki', 'attachments')
