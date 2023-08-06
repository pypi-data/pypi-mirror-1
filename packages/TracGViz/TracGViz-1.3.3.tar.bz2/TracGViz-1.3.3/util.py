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

r"""Helper (abstract) classes used to implement custom data sources,
formatters, and protocol handlers.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

__all__ = 'BaseGVizHandler', 'GVizXMLRPCAdapter', 'dummy_request', \
          'convert_req_date', 'rpc_to_datetime', 'render_gviz_value', \
          'get_column_desc', 'TYPES_2_GVIZ', 'get_column_desc', \
          'rpc_opt_sigs', 'REQFIELDS_DESC', 'REQFIELDS_DEFAULTS'

from trac.core import Component, ExtensionPoint, implements
from trac.config import Option
from trac.web.api import RequestDone, Request
from trac.web.chrome import Chrome
from trac.web.main import RequestDispatcher

from tracrpc.api import XMLRPCSystem, Method

from BaseHTTPServer import DEFAULT_ERROR_MESSAGE, BaseHTTPRequestHandler
from datetime import datetime, date, time
from itertools import takewhile, chain, imap, repeat, izip
from xmlrpclib import DateTime

from api import IGVizProtocolHandler, IGVizTableEncoder, \
                IGVizDataProvider, IHashLibrary, GVizBadRequestError

__metaclass__ = type

def send_response(req, status, response, mimetype='text/plain', \
                    extra_headers=dict()):
    r"""Send an HTTP response back to the caller.
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
    r"""Send an HTTP error response back to the caller using a 
    standard template.
    """
    message, explain = BaseHTTPRequestHandler.responses[status]
    errctx = dict(code=status, message=message, explain=explain)
    send_response(req, status, DEFAULT_ERROR_MESSAGE % errctx, \
                    mimetype='text/html')

class BaseGVizHandler(Component):
    r"""This class encloses the functionality which might be present
    in most versions of Google Visualization API. It can be reused by
    specific subclasses implementing a specific protocol version
    as defined by the Google Visualization API.
    """
    abstract = True
    implements(IGVizProtocolHandler)
    encoders = ExtensionPoint(IGVizTableEncoder)
    hashlibs = ExtensionPoint(IHashLibrary)
    
    hash_name = Option('gviz', 'hash', default=None, 
                        doc="""The algorithm used to generate a hash """
                            """of the data sent back to the client. This """
                            """feature is defined by Google """
                            """Visualization API since version 0.5 so as """
                            """to optimize the request / response """
                            """mechanism to make rational use of the """
                            """available bandwith.""")
    
    def _init_hash(self):
        r"""Setup the secure hash algorithm.
        """
        hash_name = self.hash_name
        self._hlib = self.hash_obj = None
        self.log.debug("IG: Config hash method : '%s'", hash_name)
        if hash_name:
          pr = -1
          for hlib in self.hashlibs:
            self.log.debug("IG: Processing : %s", hlib)
            try:
              cur_pr, _ = hlib.get_hash_properties(hash_name)
            except TypeError:
              self.log.debug("IG: %s doesnt support '%s'", hlib, hash_name)
            else:
              if cur_pr > pr:
                self._hlib = hlib
                pr = cur_pr
        if self._hlib is not None:
          self.hash_obj = self._hlib.new_hash_obj(hash_name)
          self.log.info("IG: Hash method '%s' lib '%s'", hash_name, self._hlib)
        else:
          self.log.info("IG: Hash method 'None'")
    
    @staticmethod
    def fmt_supports_version(encoder, version):
        r"""Return whether a data table encoder supports a specific
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
        r"""Find an encoder able to convert a data table contents into
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

#class Method(Method):
#    r"""A faster XML-RPC method implementation since it returns 
#    iterators instead of lists.
#    """
#    def __call__(self, req, args):
#        req.perm.assert_permission(self.permission)
#        result = self.callable(req, *args)
#        # If result is null, return a zero
#        if result is None:
#            result = 0
#        elif isinstance(result, dict):
#            for key,val in result.iteritems():
#                if isinstance(val, datetime.datetime):
#                    result[key] = to_datetime(val)
#            #pass
#        elif not isinstance(result, basestring):
#            # Try and convert result to a list
#            try:
#                result = (i for i in result)
#            except TypeError:
#                pass
#        return (result,)

class RPCHelperObject:
    r"""A proxy class needed to assert the permissions handled by 
    XMLRPCSystem, instead of using directly to the RPC method.
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
        r"""Try to retrieve the XML-RPC method first. Otherwise return 
        the attribute of the underlying XML-RPC object.
        """
        try:
            return self.__methods[attrnm]
        except KeyError:
            return getattr(self.__rpc_obj, attrnm)

class GVizXMLRPCAdapter(Component):
    r"""Base class for components whose main purpose is to provide 
    some data relying on an existing XML-RPC handler (i.e. a 
    component implementing tracrpc.api.IXMLRPCHandler interface). 
    The data source is meant to reuse the RPC provider namespace and
    logic.
    """
    implements(IGVizDataProvider)
    abstract = True
    
    def __init__(self):
        r"""Assign the corresponding XML RPC handler to this data
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
    rd = RequestDispatcher(env)
    chrome = Chrome(env)
    req.callbacks.update({
        'authname': rd.authenticate,
        'chrome': chrome.prepare_request,
        'hdf': rd._get_hdf,
        'perm': rd._get_perm,
        'session': rd._get_session,
        'tz': rd._get_timezone,
        'form_token': rd._get_form_token
    })
    return req

def convert_req_date(when, fmt, req, xmlfmt=True):
    r"""Convert a string to the corresponding datetime value using 
    the specified format string.
    """
    try:
      if when is not None:
          when = datetime.strptime(when, fmt)
          when = when.replace(tzinfo=req.tz)
      else:
          when = datetime.now(tz=req.tz)
      if xmlfmt:
          when = DateTime(when)
      return when
    except:
      raise GVizBadRequestError("Invalid datetime value or wrong date format.")

def rpc_to_datetime(DT, req):
    r"""Return the datetime object representing the xmlrpclib.DateTime 
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

DEFAULT_DATE_FORMATS = {
    'date' : "%Y-%m-%d",
    'datetime' : "%Y-%m-%d %H:%M:%S",
    'timeofday' : "%H:%M:%S",
  }

def render_gviz_value(value, gviz_type, table, req_or_env):
  r"""Return a string used to display the values inside GViz data 
  sources.
  """
  if isinstance(req_or_env, Request):
    req = req_or_env
  else:
    # Assume it's an instance of Environment
    req = dummy_request(req_or_env)
  try:
    date_fmt_str = DEFAULT_DATE_FORMATS[gviz_type]
  except KeyError:
    return table.SingleValueToJS(value, gviz_type)
  else:
    try:
      if isinstance(value, DateTime):
        value = rpc_to_datetime(value, req)
      elif isinstance(value, int):
        value = datetime.fromtimestamp(int(value or 0), req.tz)
      return value.strftime(date_fmt_str)
    except Exception, exc:
      return '(Unknown: %s)' % (exc,)

TYPES_2_GVIZ = {
            type(None): 'string',
            str : 'string',
            unicode : 'string',
            long : 'number',
            int : 'number',
            datetime : 'datetime',
            date : 'date', 
            time : 'timeofday',
            DateTime : 'datetime',
            bool : 'boolean',
          }

def get_column_desc(cursor, infer=False):
  r"""Retrieve a sequence of tuples (name, type) describing 
  the columns present in the results provider by a cursor object 
  after executing a database query.
  """
  row = None
  if cursor.description:
    for i, d in enumerate(cursor.description):
      name, type_code = d[:2]
      if isinstance(name, str):
        name = unicode(name, 'utf-8')
      if type_code is None and infer:
        if row is None:
          try:
            row, = cursor.fetchmany(1)
          except:
            row = ('',) * len(list(cursor.description))
        type_code = TYPES_2_GVIZ.get(row[i].__class__)
      yield name, type_code

def rpc_opt_sigs(ret_type, fixed_types=None, *opt_types):
  r"""Generate tuples describing the signatures of an XML-RPC method 
  whose arguments can take values in a set of optional types or 
  be missing in the method call.
  """
  if fixed_types is None:
    fixed_types = ()
  else:
    fixed_types = tuple(fixed_types)
  
  new_sig = (ret_type,) + fixed_types
  yield new_sig
  old_gen = [new_sig]
  
  for arg_types in opt_types:
    new_gen = []
    for sig in old_gen:
      for arg_type in arg_types:
        new_sig = sig + (arg_type,)
        yield new_sig
        new_gen.append(new_sig)
    old_gen = new_gen

REQFIELDS_DESC = {
      'datefmt'  : "The syntax of %(args)s field%(plural)s. Here you "
                            "can embed the directives supported by "
                            "`time.strftime` function. The default "
                            "behavior is to accept the well known "
                            "format `yyyy-mm-dd HH:MM:SS` which is "
                            "actually written like this "
                            "`%%Y-%%m-%%d %%H:%%M:%%S`.",
    }

REQFIELDS_DEFAULTS = {
      'datefmt'  : "%Y-%m-%d %H:%M:%S"
    }

