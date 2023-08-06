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

r"""Protocol handlers for the different versions of Google 
Visualization API.

Supported versions : 0.5

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

from trac.core import Interface, Component, ExtensionPoint, implements
from trac.config import Option
from trac.env import IEnvironmentSetupParticipant
from trac.perm import PermissionError
from trac.util import get_pkginfo
from trac.web.api import IRequestHandler
from pkg_resources import resource_string, resource_filename

# from babel.support import Translations
from os import listdir, environ
from os.path import isdir

from api import IGVizProtocolHandler
from util import BaseGVizHandler, send_response

# GViz-specific exceptions
from api import GVizDataNotModifiedError, GVizNotSupported, \
                GVizUnknownProvider, GVizDataNotModifiedError, \
                GVizBadRequest, GVizNotAuthenticatedError

JSON_MIME_TYPE = 'text/plain'

class GViz_0_5(BaseGVizHandler):
    r"""Implementation of the Google Visualization API data source
    protocol (version 0.5)
    """
    # implements(IGvizProtocolHandler)
    
    # IGvizProtocolHandler methods
    def get_version(self):
        """ Return (0, 5) to denote the supported protocol version.
        """
        return (0, 5)
    
    def get_std_params(self):
        r"""Return a mapping containing the following values :
        
        reqId = 0, 
        version = '0.5', 
        sig = None,
        out = 'json', 
        responseHandler = 'google.visualization.Query.setResponse'
        """
        return {'reqId' : 0, 'version' : '0.5', 'sig' : None,
                'out' : 'json', 
                'responseHandler' : 'google.visualization.Query.setResponse'}
    
    ERROR_LABELS = {
                    GVizDataNotModifiedError : \
                            ['not_modified', 'Data not modified'],
                    GVizNotAuthenticatedError : \
                            ['user_not_authenticated', \
                            'Trac : Authentication required'],
                    PermissionError : \
                            ['access_denied', 'Access Denied'],
                    GVizNotSupported : \
                            ['not_supported', 'Not supported'],
                    GVizUnknownProvider : \
                            ['unknown_data_source_id', 'Not Found'],
                    GVizBadRequest : \
                            ['invalid_request', 'Bad request']
                   }
    
    def _error(self, req, error, reqId, version, responseHandler):
        """Send an error response back to the client.
        """
        values = dict(v=version, h=responseHandler, rId=reqId)
        if isinstance(error, tuple):
            error, tb = error
            while tb.tb_next:
                tb = tb.tb_next
        else:
            tb = None
        if isinstance(error, PermissionError) and \
                req.authname in (None, 'anonymous'):
            error = GVizNotAuthenticatedError(unicode(error))
        else:
            error.message = unicode(error)
        exc_label, exc_msg = self.ERROR_LABELS.get(error.__class__, \
                                ('other', error.__class__.__name__))
        
        values['exc'] = exc_label
        values['msg'] = exc_msg
        if tb:
            detail = "%s [%s] : " % \
                    (tb.tb_frame.f_globals.get('__name__', '<builtin>'), \
                    tb.tb_lineno)
        else:
            detail = ""
        values['d'] = (detail + error.message).replace('\'', '').replace('"', '')
        response = "%(h)s({version:'%(v)s',reqId:'%(rId)s'," \
                    "status:'error',errors:[{reason:'%(exc)s'," \
                    "message:'%(msg)s',detailed_message:'%(d)s'}]});" % values
        send_response(req, 200, response, 'text/plain')
    
    def output_response(self, _req, _table, _error=None,
                        _warnings=None, reqId=0, version='0.5', 
                        sig=None, out='json', 
                        responseHandler='google.visualization.Query.setResponse',
                        **ignored):
        r"""Send the response back to the client.
        
        @param req an object encapsulating the data submitted by
                    the client in the HTTP request.
        @param table the instance of `gviz_api.DataTable` containing
                    the data requested by the client.
  	    @param error an exception object raised while processing the
                    request or `None` otherwise.
        @param warnings a sequence of warning messages returned to 
                    the client.
        @param reqId A numeric identifier for this request.
        @param version The version number of the Google Visualization
                    protocol.
        @param sig A hash of the DataTable sent to this client in any
                    previous requests to this data source.
        @param out A string describing the format for the returned 
                    data. The following standard values are supported
                    if the corresponding formatters are enabled:
                    
                    - json [Default value] : A JSON response string
                    - html : A basic HTML table with rows and columns.
                    - csv : Comma-separated values.
                    
                    However it is possible to support more values
                    by registering new subclasses implementing the
                    `IGvizDataFormatter` interface.
        """
        self.log.debug("IG: Requested format %s", out)
        if _error is not None:
            self._error(_req, _error, reqId, version, responseHandler)
        e = self.find_encoder(out, self.get_version())
        if e is not None:
            contents = e.stream_contents(_table)
            if out == 'json':
                if sig is not None and self.hash_obj is not None:
                    hash_obj = self.hash_obj.copy()
                    hash_obj.update(contents)
                    hash_str = hash_obj.hexdigest()
                    if hash_str == sig:
                        exc = GVizDataNotModifiedError('')
                        self._error(_req, exc, reqId, version, responseHandler)
                    hash_str = "'sig':'%s'," % (hash_str,)
                else:
                    hash_str = ""
                contents = "%(h)s({'version':'%(v)s', " \
                        "'reqId':'%(rId)s', 'status':'ok', " \
                        "%(hash)s 'table': %(data)s});" % \
                                dict(h=responseHandler, rId=reqId, 
                                        v=version, data=contents,
                                        hash=hash_str)
            send_response(_req, 200, contents, \
                                mimetype=e.get_content_type())
        else:
            exc = GVizNotSupported('Invalid format id %s' % (out,))
            self._error(_req, exc, reqId, version, responseHandler)
