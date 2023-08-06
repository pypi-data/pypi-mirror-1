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

r"""Table encoders for non-standard Google Visualization API formats.

Supported formats : 

- version 0.5 : MoinMoin wiki formatting (e.g. like Trac), 
  reStructuredText

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

__all__ = 'GVizMoinEncoder',

from trac.core import Component, implements
from api import IGVizTableEncoder
from util import render_gviz_value

class GVizMoinEncoder(Component):
    """MoinMoin wiki encoder for Google Visualization API.
    """
    implements(IGVizTableEncoder)
    
    def supported_versions(self):
        """Support Google Visualization API version 0.5 and superior.
        """
        yield ('>=', (0, 5))
    
    def stream_contents(self, table, params={}):
        r"""Encode a table using MoinMoin wiki formatting.
        
        @param table the target instance of `gviz_api.DataTable`.
        """
        columns = table.columns
        out = '||'.join(col_desc['label'].replace('||', '| |') \
                        for col_desc in columns)
        out = '||%s||\n' % (out,)
        columns_order = [col["id"] for col in columns]
        col_dict = dict([(col["id"], col) \
                            for col in table._DataTable__columns])
        
        def rowvalues(row):
          for col in columns_order:
            # Do not display None values
            value = row.get(col, None)
            if value is None:
              yield ""
            else:
#              value = table.SingleValueToJS(value, col_dict[col]["type"])
              value = render_gviz_value(value, col_dict[col]["type"], \
                                        table, self.env)
              for changes in [('||', '| |'), ('\n', ' '), ('\r', ' '),]:
                value = value.replace(*changes)
              if isinstance(value, tuple):
                # We have a formatted value as well ... show it
                value = value[1]
              yield value
        
        for row in table._PreparedData(()):
            out+= '||'
            out+= '||'.join(value for value in rowvalues(row))
            out+= '||\n'
        return out
    
    def get_format_id(self):
        """Return 'moin'.
        """
        return 'moin'
    
    def get_content_type(self):
        """MIME-type in this case is `text/plain` AFAIK.
        """
        # TODO : Return more suitable mime type
        return 'text/plain'

class GVizRstEncoder(Component):
    """reStructuredText encoder for Google Visualization API.
    """
    implements(IGVizTableEncoder)
    
    def supported_versions(self):
        """Support Google Visualization API version 0.5 and superior.
        """
        yield ('>=', (0, 5))
    
    def stream_contents(self, table, params={}):
        r"""Encode a table to reStructuredText format.
        
        @param table the target instance of `gviz_api.DataTable`.
        """
        return "Not implemented yet"
    
    def get_format_id(self):
        """Return 'moin'.
        """
        return 'rst'
    
    def get_content_type(self):
        """MIME-type in this case is `text/plain` AFAIK.
        """
        # TODO : Return more suitable mime type
        return 'text/plain'

