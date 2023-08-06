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

"""Table encoders for standard Google Visualization API formats.

Supported formats : 

- version 0.5 : JSON, CSV, HTML

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

from trac.core import Component, implements
from api import IGVizTableEncoder

# TODO : Implement order by and select statements

class GVizJsonEncoder(Component):
    """JSON encoder for Google Visualization API.
    """
    implements(IGVizTableEncoder)
    
    def supported_versions(self):
        """Support Google Visualization API version 0.5 and superior.
        """
        yield ('>=', (0, 5))
    
    def stream_contents(self, table, params={}):
        """Table to JSON.
        
        @param table the target instance of `gviz_api.DataTable`.
        """
        return table.ToJSon()
    
    def get_format_id(self):
        """Return 'json'.
        """
        return 'json'
    
    def get_content_type(self):
        """MIME-type in this case is `application/json`.
        """
        return 'application/json'

class GVizHtmlEncoder(Component):
    """HTML encoder for Google Visualization API.
    """
    implements(IGVizTableEncoder)
    
    def supported_versions(self):
        """Support Google Visualization API version 0.5 and superior.
        """
        yield ('>=', (0, 5))
    
    def stream_contents(self, table, params={}):
        """Table to HTML.
        
        @param table the target instance of `gviz_api.DataTable`.
        """
        out = "<html><body><table border='1' cellpadding='2' " \
                "cellspacing='0'><tr style='font-weight: bold; " \
                "background-color: #aaa;'>"
        columns = table.columns
        for col_desc in columns:
            out+= "<td>%s</td>" % (col_desc['label'],)
        out+= "</tr>"
        
        columns_order = [col["id"] for col in columns]
        col_dict = dict([(col["id"], col) \
                        for col in table._DataTable__columns])
        for i, row in enumerate(table._PreparedData(())):
          out+= "<tr bgcolor='%s'>" % ((i & 1) and '#f0f0f0' or '#ffffff',)
          for col in columns_order:
            # Do not display None values
            value = row.get(col, None)
            if value is None:
              value = ""
            else:
              value = table.SingleValueToJS(value, col_dict[col]["type"])
              # TODO: Sanitize in case of HTML string
              if isinstance(value, tuple):
                # We have a formatted value as well ... show it
                value = value[1]
            out+= "<td>%s</td>" % (value,)
          out+= "</tr>"
        out+= "</table></body></html>"
        return out
    
    def get_format_id(self):
        """Return 'html'.
        """
        return 'html'
    
    def get_content_type(self):
        """MIME-type in this case is `text/html`.
        """
        return 'text/html'

class GVizCSVEncoder(Component):
    """CSV encoder for Google Visualization API.
    """
    implements(IGVizTableEncoder)
    
    def supported_versions(self):
        """Support Google Visualization API version 0.5 and superior.
        """
        yield ('>=', (0, 5))
    
    def stream_contents(self, table, params={}):
        """Encode a table using to Comma Separated Values.
        
        @param table the target instance of `gviz_api.DataTable`.
        """
        columns = table.columns
        out = ",".join(col_desc['label'] for col_desc in columns)
        out+= '\n'
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
              value = table.SingleValueToJS(value, col_dict[col]["type"])
              if isinstance(value, tuple):
                # We have a formatted value as well ... show it
                value = value[1]
              yield value
        
        for row in table._PreparedData(()):
            out+= ','.join(value for value in rowvalues(row))
            out+= '\n'
        return out
    
    def get_format_id(self):
        """Return 'csv'.
        """
        return 'csv'
    
    def get_content_type(self):
        """MIME-type in this case is `text/comma-separated-values`.
        """
        return 'text/comma-separated-values'

