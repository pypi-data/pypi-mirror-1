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

"""Helper (abstract) classes used to implement custom data sources,
formatters, and protocol handlers.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

__all__ = 'BaseGVizHandler', 'GVizXMLRPCAdapter', 'dummy_request'

from trac.core import Interface, Component, ExtensionPoint, implements, \
                        TracError
from trac.config import Option
from trac.util import get_pkginfo
from trac.web.api import IRequestHandler, RequestDone, Request
from trac.web.main import RequestDispatcher
from pkg_resources import resource_string, resource_filename

from tracrpc.api import XMLRPCSystem, Method

# from babel.support import Translations
from BaseHTTPServer import DEFAULT_ERROR_MESSAGE, BaseHTTPRequestHandler
from datetime import datetime
import hashlib
from itertools import takewhile, chain, imap, repeat, izip
from os import listdir, environ
from os.path import isdir
import types
from xmlrpclib import DateTime

from api import IGVizProtocolHandler, IGVizTableEncoder, \
                IGVizDataProvider

__metaclass__ = type

def send_response(req, status, response, mimetype='text/plain', \
                    extra_headers=dict()):
    """Send an HTTP response back to the caller.
    """
    req.send_response(status)
    req.send_header('Content-Type', mimetype)
    req.send_header('Content-Length', len(response))
    for k, v in dict(extra_headers).iteritems():
        req.send_header(k, v)
    req.end_headers()
    req.write(response)
    raise RequestDone()

def send_std_error_response(req, status):
    """Send an HTTP error response back to the caller using a 
    standard template.
    """
    message, explain = BaseHTTPRequestHandler.responses[status]
    errctx = dict(code=status, message=message, explain=explain)
    send_response(req, status, DEFAULT_ERROR_MESSAGE % errctx, \
                    mimetype='text/html')

class BaseGVizHandler(Component):
    """This class encloses the functionality which might be present
    in most versions of Google Visualization API. It can be reused by
    specific subclasses implementing a specific protocol version
    as defined by the Google Visualization API.
    """
    abstract = True
    implements(IGVizProtocolHandler)
    encoders = ExtensionPoint(IGVizTableEncoder)
    
    hash_name = Option('gviz', 'hash', default=None, 
                        doc="""The algorithm used to generate a hash """
                            """of the data sent back to the client. This """
                            """feature is defined by Google """
                            """Visualization API since version 0.5 so as """
                            """to optimize the request / response """
                            """mechanism to make rational use of the """
                            """available bandwith.""")
    
    __std_hash_names = [x for x in hashlib.__dict__ 
                                if not x.startswith('_') and x!= 'new']
    default_hash_names = property(lambda self: self.__std_hash_names)
    
    def _init_hash(self):
        """Setup the secure hash algorithm.
        """
        hash_name = self.hash_name
        if hash_name is None:
            self.hash_obj = None
        elif hash_name in self.default_hash_names:
            self.hash_obj = getattr(hashlib, hash_name)()
        else:
            # Perhaps other algorithm supported by local OpenSSL library
            try:
                self.hash_obj = hashlib.new(hash_name)
            except ValueError, exc:
                self.log.debug('IG: Could not setup hash algorithm'
                                    'for class %s', self.__class__.__name__)
                self.hash_obj = None
        self.log.debug('IG: Hash object for class %s: %s', 
                        self.__class__.__name__, self.hash_obj)
    
    @staticmethod
    def fmt_supports_version(encoder, version):
        """Return whether a data table encoder supports a specific
        version of Google Visualization API."""
        
        rels = {
                '>' : tuple.__gt__,
                '<' : tuple.__lt__,
                '>=' : tuple.__ge__,
                '<=' : tuple.__le__,
                '==' : tuple.__eq__,
                '!=' : lambda x, y: x != y,
               }
        
        versions = encoder.supported_versions()
        return all(rels[r](v, version) for r, v in versions)
    
    def find_encoder(self, fmt_id, version, mime_type=None):
        """Find an encoder able to convert a data table contents into
        a specific format, maybe having a well-known content-type.
        
        @param fmt_id the output format id
        @param version the particular protocol `version` of Google
                    Visualization API in use.
        @param mime_type if specified then a best match is made to 
                    return an encoder returning the specific content
                    type requested by the caller.
                    
        @return the best match made according to the available 
                    encoders or `None` if no such encoder could be
                    found. This encoder *must* support the requested
                    format and protocol version, and *should*
                    use the requested content-type, but the later
                    assertion *is not compulsory*.
        """
        encoders = self._fmt[fmt_id]
        encoders = takewhile(
                lambda e: self.fmt_supports_version(e, version), 
                encoders)
        try:
            first = encoders.next()
        except StopIteration:
            return None
        else:
            if mime_type is None or first.get_content_type() == mime_type:
                return first
            else:
                try:
                    return takewhile(
                            lambda e: e.get_content_type() == mime_type, 
                            encoders).next()
                except StopIteration:
                    return first
    
    def _init_fmt(self):
        """Arrange the available format encoders.
        """
        self._fmt = dict()
        for e in self.encoders:
            self._fmt.setdefault(e.get_format_id(), []).append(e)
    
    def __init__(self):
        self._init_fmt()
        self._init_hash()
        
    # TODO : Implement common features.

class VoidRpcHandler:
    def __getattr__(self, attrnm):
        raise AttributeError("The requested XML-RPC handler cannot "
                                "be found. Either it doesn't exist "
                                "or the component is disabled. "
                                "Contact your Trac administrator.")

class RPCHelperObject:
    """A proxy class needed to assert the permissions handled by 
    XMLRPCSystem, instead of going directly to the RPC method.
    """
    def __init__(self, rpc_obj):
        methods = (Method(rpc_obj, *mi) for mi in rpc_obj.xmlrpc_methods())
        prefix_len = len(rpc_obj.xmlrpc_namespace()) + 1
        
        def method_wrapper(m):
            wrapper = lambda req, *args: m(req, args)[0]
            wrapper.__module__ = m.callable.__module__
            wrapper.func_name = m.callable.__name__
            return wrapper
        self.__methods = dict([m.name[prefix_len:], method_wrapper(m)] \
                                for m in methods)
        rpc_obj.log.debug('IG: RPC methods %s', self.__methods)
        self.__rpc_obj = rpc_obj
    
    def __getattr__(self, attrnm):
        """Try to retrieve the XML-RPC method first. Otherwise return 
        the attribute of the underlying XML-RPC object.
        """
        try:
            return self.__methods[attrnm]
        except KeyError:
            return getattr(self.__rpc_obj, attrnm)

class GVizXMLRPCAdapter(Component):
    """Base class for components whose main purpose is to provide 
    some data relying on an existing XML-RPC handler (i.e. a 
    component implementing tracrpc.api.IXMLRPCHandler interface). 
    The data source is meant to reuse the RPC provider namespace and
    logic.
    """
    implements(IGVizDataProvider)
    abstract = True
    
    def __init__(self):
        """Assign the corresponding XML RPC handler to this data
        source provider. 
        
        Note: Since Trac core system components hack the initializer,
        further initialiation steps needed by sub-classes should be
        coded by overriding `do_init` method.
        """
        try:
            rpcns = '.'.join(self.xmlrpc_namespace())
        except AttributeError:
            rpcns = '.'.join(self.gviz_namespace())
        self.log.debug('IG: RPC Namespace %s Ok', rpcns)
        for rpc_provider in XMLRPCSystem(self.env).method_handlers:
            # TODO : Implement a proper match for regex in gviz ns
            if rpc_provider.xmlrpc_namespace() == rpcns:
                # Substituted in order to reuse permissions asserted 
                # by XMLRPCSystem.
                # self._rpc_obj = rpc_provider
                self._rpc_obj = RPCHelperObject(rpc_provider)
                break
        else:
            self._rpc_obj = VoidRpcHandler()
            self.log.info('IG: Missing XML-RPC handler %s' % (rpcns,))
        try:
            __init__ = self.do_init
        except AttributeError:
            pass
        else:
            __init__()

def dummy_request(env):
    environ = {
                'trac.base_url' : str(env._abs_href('gviz')), 
                'SCRIPT_NAME' : str(env._abs_href('gviz'))
                }
    req = Request(environ, lambda *args, **kwds: None)
    req.callbacks['perm'] = RequestDispatcher(env)._get_perm
    return req

def convert_req_date(when, fmt, req, xmlfmt=True):
    """Convert a string to the corresponding datetime value using 
    the specified format string.
    """
    if when is not None:
        when = datetime.strptime(when, fmt)
        when = when.replace(tzinfo=req.tz)
    else:
        when = datetime.now(tz=req.tz)
    if xmlfmt:
        when = DateTime(when)
    return when

def rpc_to_datetime(DT, req):
    """Return the datetime object representing the xmlrpclib.DateTime 
    value in `DT`. The return value is at the timezone of the 
    environment processing the request `req`.
    """
    dt = datetime.strptime(DT.value, '%Y%m%dT%H:%M:%S')
    return dt.replace(tzinfo=req.tz)

def __insert_many_id(id, _tuple): 
    return (id,) + _tuple

def __insert_value_id(id, value): 
    return (id, value)

def map_with_id(req, ids, func, ins, *iterables):
    if iterables:
        iterables = izip(*iterables)
    else:
        iterables = repeat(tuple())
    return chain(*(imap(ins, repeat(x), func(req, x, *args)) \
            for x, args in izip(ids, iterables)))

def map_many_with_id(req, ids, func, *iterables):
    return map_with_id(req, ids, func, __insert_many_id, *iterables)

def map_value_with_id(req, ids, func, *iterables):
    return map_with_id(req, ids, func, __insert_value_id, *iterables)

