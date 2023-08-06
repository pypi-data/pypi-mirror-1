
#   Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
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

r"""Data sources used to publish the data provided by the different 
sources for timed events contributing to the timeline.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0
"""

__all__ = 'GVizTimelineEvents', 'GVizTimelineFilters'

import types

from api import gviz_col, gviz_param
from util import GVizXMLRPCAdapter, rpc_to_datetime, convert_req_date, \
                  REQFIELDS_DESC, REQFIELDS_DEFAULTS

class GVizTimelineEvents(GVizXMLRPCAdapter):
    r"""Return the timed events contributed to the timeline.
    
    This component depends on tracgviz.timeline.TimelineRPC. The later
    must be enabled. Please read
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    
    Note: In order to retrieve all events related to ticket 
          changes (e.g. attachments) you need to set
          timeline.ticket_show_details option in trac.ini to true.
    """
    # IGVizDataProvider methods
    def get_data_schema(self):
        return [('kind', 'string'), ('author', 'string'), \
                ('date', 'datetime'), ('timestamp', 'number'), \
                ('url', 'string'), ('title', 'string'), \
                ('description', 'string')]

    @gviz_col('kind', "A string categorizing the event.")
    @gviz_col('author', "The agent (user) that's performing the action.")
    @gviz_col('date', "The time when the event took place.")
    @gviz_col('timestamp', "Timestamp indicating the seconds ellapsed "
                            "since the moment the event took place "
                            "(counting from the epoc).")
    @gviz_col('url', "The changes can be viewed at this URL.")
    @gviz_col('title', "A short text illustrating the resource and "
                        "the changes made.")
    @gviz_col('description', "A textual description of the changes.")
    @gviz_param('start', "Return events that took place after this "
                            "date. Defaults to the epoc 1970-1-1.")
    @gviz_param('stop', "Return the events that took place before this "
                            "date. Defaults to the time when the "
                            "request is being processed.")
    @gviz_param('fmt', REQFIELDS_DESC['datefmt'] % \
                            dict(args='both `start` and `stop`', \
                                  plural='s'))
    @gviz_param('filter', "The name of the filter to be enabled. This "
                            "field may be specified more than once "
                            "in order to select multiple filters.")
    def get_data(self, req, tq, start=None, stop=None, \
                    fmt=REQFIELDS_DEFAULTS['datefmt'], filter=None, **tqx):
        r"""Retrieve ticket actions.
        """
        if isinstance(filter, types.StringTypes):
            filter = [filter]
        if start is not None:
            start = convert_req_date(start, fmt, req)
        if stop is not None:
            stop = convert_req_date(stop, fmt, req)
        return self._rpc_obj.getEvents(req, start, stop, filter)

    def xmlrpc_namespace(self):
        """Use Ticket XML-RPC.
        """
        return ('timeline',)
    def gviz_namespace(self):
        return ('timeline', 'log')

class GVizTimelineFilters(GVizXMLRPCAdapter):
    r"""Return the the available filters provided by the different 
    sources contributing to the timeline.
    
    This component depends on tracgviz.rpc.TimelineRPC. The later
    must be enabled. Please read
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    # IGVizDataProvider methods
    def get_data_schema(self):
        return [('id', 'string'), ('name', 'string')]
    
    @gviz_col('id', "The string used to identify the event filter.")
    @gviz_col('text', "The display name of this filter.")
    def get_data(self, req, tq, filter=None, **tqx):
        """Retrieve timeline filters.
        """
        return self._rpc_obj.getEventFilters(req)

    def xmlrpc_namespace(self):
        """Use Timeline XML-RPC.
        """
        return ('timeline',)
    def gviz_namespace(self):
        return ('timeline', 'filters')

