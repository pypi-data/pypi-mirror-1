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

r"""Trac Data Source able to feed widgets implemented with Google Visualization API.

Components allowing Trac to export a project (environment)'s data so
that different widgets based on Google Visualization (GViz) API
be able to use that information in order to render a web GUI item.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

from trac.core import Interface, Component, ExtensionPoint, \
                      implements
from trac.perm import IPermissionRequestor, PermissionError
from trac.util.datefmt import utc
from trac.web.api import IRequestHandler, RequestDone
from trac.web.chrome import ITemplateProvider

from pkg_resources import resource_filename

try:
    import gviz_api
except ImportError:
    import _gviz_api as gviz_api
import sys
from xmlrpclib import DateTime
from datetime import datetime

class GVizException(Exception):
  r"""Base class for all exception types defined in this package"""

class GVizProviderNotFoundError(GVizException):
    r"""Exception raised to denote that there is no GViz provider able
    to handle the request.
    """

class GVizNotSupportedError(GVizException):
    r"""Exception raised to denote that an unsopported feature has been
    requested by the client.
    """

class GVizBadRequestError(GVizException):
    r"""Exception raised to denote that the client request contains 
    wrong fields and/or values, or that required data is missing.
    """

class GVizUnknownProviderError(GVizException):
    r"""Exception raised to denote that there is no provider able to
    to handle the client request.
    """

class GVizNotAuthenticatedError(GVizException):
    r"""Exception raised when a permission error is detected while 
    processing an anonymous request.
    """

class GVizDataNotModifiedError(GVizException):
    r"""Exception raised when the hash generated from the data
    returned by the GViz provider matches the hash value sent by the 
    client.
    """
    message = ''

class GVizInvalidConfigError(GVizException):
    r"""Exception raised when an invalid, incorrect or unsupported 
    value has been assigned to a configuration option.
    """

def gviz_col(col_id, col_doc):
    r"""This function can be used to document the meaning of the 
    different columns in the table returned by GViz data sources as 
    well as the default label and column order. This function is 
    compliant with annotations as defined by PEP 3107.
    """
    def decorator(func):
        try:
            anns = func.func_annotations
        except AttributeError:
            func.func_annotations = {'return' : \
                    {col_id: col_doc}}
        else:
            anns.setdefault('return', {})[col_id] = col_doc
        return func
    return decorator

def gviz_param(name, doc):
    r"""This function can be used to document the meaning of the 
    different parameters accepted by GViz data sources as 
    well as their default values. 
    This function is compliant with annotations as defined by PEP 3107.
    """
    if name == 'return':
        return lambda f: f
    def decorator(func):
        try:
            anns = func.func_annotations
        except AttributeError:
            func.func_annotations = {name : doc}
        else:
            anns[name] = doc
        return func
    return decorator

class IGVizDataProvider(Interface):
    r"""All the components providing GViz data tables to clients
    ought to implement this interface.
    """
    def gviz_namespace():
        r""" Provide the path to access this data source provider.
        This is used to determine the URL clients will retrieve
        the data from.
        
        Return a list of items, each one being a string denoting
        either a path handle or a regular expression used to 
        match the requested path. Each such item *must not* match a
        string containing the slash (i.e. `/`) character.
        
        Note : regex in path handles are not supported yet.
        """
    
    def get_data_schema(req=None):
        r"""Provide the schema used to populate GViz data tables out 
        of the Python object containing the table contents.
        
        @req    (since version 1.3.3) an optional argument that can 
                be used by data providers offering data in different 
                ways depending upon the values provided at run-time 
                for some parameters. If this function has more than 
                a single argument then it *MUST* be the request 
                being processed.
        @return schema definition used to prepare the data table. See 
                the documentation for `gviz_api.DataTable` class for 
                more details about schemas.
        """
    
    def get_data(req, tq, **tqx):
        r""" Return a Python object containing all the data to be
        returned to the client so as to fill a data table object.
        
        @param tq the query requested by the client.
        @param req the query requested by the client.
        @param tqx custom arguments specified by the client. Every 
                    standard parameter defined by the Visualization
                    protocol (see the values in
                    `TracGVizSystem.reserved_args`) is removed since
                    they have special meanings no matter what data
                    is provided by a specific GViz data source.
        """

class IGVizProtocolHandler(Interface):
    r"""All components implementing a specific version of the Google
    Visualization Protocol must implement this interfaces.
    """
    def get_version():
        r""" Return a tuple like (epoch, major[, minor]) representing
        the protocol version implemented by the component.
        """
    
    def get_std_params():
        r"""Return a mapping object representing the parameters having
        special meanings according to the protocol specification.
        The mapping keys should be the name of the parameter, whereas
        the mapping values should be the parameter's default value.
        """
    
    def output_response(_req, _table, _error=None,
                        _warnings=None, **std_params):
        r"""Send the response back to the client.
        
        @param req an object encapsulating the data submitted by
                    the client in the HTTP request.
        @param table the instance of `gviz_api.DataTable` containing
                    the data requested by the client.
        @param error an exception object raised while processing the
                    request or `None` otherwise.
        @param warnings a sequence of warning messages returned to 
                    the client.
        @param std_params the values bound to the standard parameters
                    in the request string.
        """

class DataTable(gviz_api.DataTable):
    r"""Tries to fix the incompatibilities between xmlrpclib and 
    gviz_api modules.
    """
    @staticmethod
    def SingleValueToJS(value, value_type):
        r"""Translates a single value and type into a JS value, but 
        trying to fix the incompatibilities between xmlrpclib and 
        gviz_api modules.
        """
        if value_type in ["date", "datetime", "timeofday"] and \
                isinstance(value, DateTime):
            value = datetime.strptime(value.value, '%Y%m%dT%H:%M:%S')
        if value_type in ["date", "datetime", "timeofday"] and \
                isinstance(value, int):
            value = datetime.fromtimestamp(int(value or 0), utc)
        elif value_type == "string" and isinstance(value, unicode):
            value = value.encode('utf-8', 'replace')
        return gviz_api.DataTable.SingleValueToJS(value, value_type)

class TracGVizSystem(Component):
    r"""A component responsible for dispatching requests addressed to 
    the different GViz data sources available in the system. The 
    requests processed by the appropriate provider return a response 
    back to the client conforming to the formats supported by Google 
    Visualization API. By default it should return data in 
    `JSON Response Format`, but this decision is delegated to the 
    underlying protocol implementation.
    """
    implements(IRequestHandler, ITemplateProvider, \
                IPermissionRequestor)
    providers = ExtensionPoint(IGVizDataProvider)
    handlers = ExtensionPoint(IGVizProtocolHandler)
    
    def __init__(self):
        self._cache = dict(['/gviz/' + '/'.join(p.gviz_namespace()), p] \
                        for p in self.providers)
        self.log.debug('IG: Providers cache %s', (self._cache,))
        self._handlers = dict( \
                ['.'.join(str(x) for x in h.get_version()), h] \
                for h in self.handlers)
        try:
            self._latest = max(h.get_version() for h in self.handlers)
        except ValueError:
            self._latest = None
        else:
            self._latest = '.'.join(str(x) for x in self._latest)
    
    # IPermissionRequestor methods
    def get_permission_actions(self):
      """Return a list of actions defined by this component."""
      yield 'GVIZ_VIEW'
    
    # IRequestHandler methods
    def match_request(self, req):
        r"""Return whether the requested path starts with `/gviz`
        prefix or not.
        """
        url_path = req.path_info
        if url_path.startswith('/gviz'):
            try:
                return url_path[5] == '/'
            except IndexError:
                return True
    
    def process_request(self, req):
        r"""Perform one of the following actions :
        
        - If the request is addressed to a specific data source then
          send back the corresponding data table's contents in one of
          the formats supported by Google Visualization API (defaults
          to JSON Response Format).
        
        - If the request is addressed directly to the `root path` (i.e. 
          req.path_info == '/gviz') then render an informative page
          displaying all the registered data sources' specification.
        
        - Else send back a `Not Found` error message.
        """
        url_path = req.path_info
        if url_path in ('/gviz', '/gviz/'):
            req.perm.require('GVIZ_VIEW')
            return 'gviz_index.html', dict(), None
        else:
            if self._latest is None:
                req.send_response(404)
                req.end_headers()
                req.write('Unable to find any protocol handler')
                raise RequestDone()
            try:
                req.perm.require('GVIZ_VIEW')
                provider = self._cache[url_path]
            except (KeyError, PermissionError), exc:
                if isinstance(exc, KeyError):
                  exc = GVizUnknownProviderError('Unknown provider "%s"' %
                                              (url_path,))
                handler = self._handlers[self._latest]
                handler.output_response(req, None, exc, None)
                raise RequestDone()
            else:
                tq = req.args.pop('tq', '')
                try:
                    params = req.args['tqx']
                    self.log.debug("IG: Plain params : %s" % (params,))
                except KeyError:
                    std_params = dict()
                    handler = self._handlers[self._latest]
                else:
                    try:
                        params = dict(i.split(':', 1) \
                                for i in str(params).split(';'))
                    except:
                        exc = GVizBadRequestError('Syntax error in "%s"' %
                                            (params,))
                        handler = self._handlers[self._latest]
                        handler.output_response(req, None, exc, \
                                                None, **std_params)
                        raise RequestDone()
                    else:
                        version = params.get('version', self._latest)
                        try:
                            handler = self._handlers[version]
                            # TODO: Provide a better match for protocol handlers
                        except KeyError, exc:
                            handler = self._handlers[self._latest]
                            exc = GVizNotSupportedError('Unsupported protocol version '
                                    '"%s"' % (exc.message,))
                            handler.output_response(req, None, exc, \
                                                    None, **std_params)
                            raise RequestDone()
                        defaults = handler.get_std_params()
                        std_params = dict([k, params.pop(k, v)] \
                                for k,v in defaults.iteritems())
                # Custom options have to be specified outside
                # tqx field (i.e. directly inside the URL), 
                # at least until further notice
                self.log.debug("IG: Request parameters : %s", req.args)
                params = dict(req.args)
                self.log.debug("IG: Custom parameters : %s", params)
                table = None
                try:
                    data = provider.get_data(req, tq, **params)
                    sch = provider.get_data_schema.im_func.func_code
                    sch_args = (sch.co_argcount > 1) and (req,) or ()
                    table = DataTable(provider.get_data_schema(*sch_args), \
                                        data)
                    handler.output_response(req, table, None, \
                                            None, **std_params)
                except RequestDone:
                    raise
                except Exception, exc:
                    self.log.exception("IG: Handling exception")
                    handler.output_response(req, table, 
                            sys.exc_info()[1:], exc, **std_params)
                    raise RequestDone()
                
                raise RequestDone()
    
    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        yield ('gviz', resource_filename('tracgviz', 'htdocs'))

    def get_templates_dirs(self):
        return [resource_filename('tracgviz', 'templates')]

class IGVizTableEncoder(Interface):
    r"""Implementing this interface is mandatory for every component
    in charge of converting a table contents into a character
    stream suitable for trasmitting it over an HTTP connection.
    """
    def supported_versions():
        r"""Return a sequence containing tuples, each one specifying
        the protocol versions supported by this format encoder. The
        tuples should be as follows :
        
        (Relationship, VersionNumber)
        
        where :
        
        Relationship := '<' | '>' | '<=' | '>=' | '==' | '!='
        VersionNumber := (Number ',' Number [',' Number])
        
        e.g. [('==', (0, 1, 2)),('==', (0, 1, 5)), 
              ('>=', (0, 2)), ('!=', (0, 4)), ('<', (1, 0))]
        """
    
    def stream_contents(table, params={}):
        r"""Convert the table contents to a format suitable for
        trasmitting them over an HTTP connection.
        
        @param table the target instance of `gviz_api.DataTable`.
        @std_params the values of the standard parameters.
        """
    
    def get_format_id():
        r"""Return the token identifying the format outputted by this 
        formatter object.
        """
    
    def get_content_type():
        r"""Return the content-type associated with this format 
        encoder.
        """

class ITracLinksHandler(Interface):
    r"""Interface implemented by those classes being
    TracLinks providers registered under the namespaces managed by
    this plugin.
    """
    def get_link_resolvers(self):
        r"""Return an iterable over (namespace, formatter) tuples.
        Namespaces value must be tuples.
        
        Each formatter should be a function of the form
        fmt(formatter, ns, target, label), and should
        return some HTML fragment.
        The `label` is already HTML escaped, whereas the `target` is not.
        """

class IHashLibrary(Interface):
  r"""Interface implemented by all those components defining one or 
  more secure hash, message digest, or checksum algorithms to be used 
  by other components.
  """
  def get_hash_properties(method_name):
    r"""Determine whether this component supports a secure hash 
    algorithm or not.
    
    @param method_name  is the name identifying the hash method
                        (e.g. sha1, md5, ...) in lowercase letters
    @return             `None` if the component does not support the 
                        requested algorithm. Otherwise, a tuple of 
                        the form (priority, source) where
                        
                        priority: is a number indicating how much 
                                  relevant is this implementation. 
                                  If multiple components support the 
                                  same method then the one specifying 
                                  the higher `priority` value will 
                                  be chosen.
                        source:   is a numeric constant identifying 
                                  the library providing the 
                                  implementation for this method. The 
                                  following values have been defined 
                                  so far:
                                  
                                  0   - implemented by the OpenSSL 
                                        library that Python uses on 
                                        your platform. 
                                  100 - implemented in Python stdlib
                                  200 - implemented in a Python module 
                                        (or C extension, ...) but not 
                                        in stdlib
    """
  def new_hash_obj(method_name, init_data):
    r"""Create a hash object.
    
    @param method_name  is the name identifying the hash method
                        (e.g. SHA1, MD5, ...)
    @param init_data    data processed since the beginning
    @return             a hash object implementing the aforementioned 
                        algorithm by means of the same 
                        simple interface defined in `hashlib` module.
    """

# TODO : Cache the requests and optimize the call/response life cycle
#            by using the `reqId` parameter.

