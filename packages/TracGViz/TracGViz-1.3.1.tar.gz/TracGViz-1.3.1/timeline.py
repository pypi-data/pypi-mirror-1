
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

"""Data sources used to publish the data provided by the different 
sources for timed events contributing to the timeline.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0
"""

__all__ = 'TimelineRPC', 'GVizTimelineEvents', 'GVizTimelineFilters'

from trac.core import implements, ExtensionPoint, Component
from trac.mimeview.api import Context
from trac.timeline.api import ITimelineEventProvider
from trac.timeline.web_ui import TimelineModule
from trac.util.datefmt import _epoc

from datetime import datetime
from itertools import chain
from tracrpc.api import IXMLRPCHandler
import types
import xmlrpclib

from api import gviz_col, gviz_param
from util import GVizXMLRPCAdapter, rpc_to_datetime, convert_req_date

class TimelineRPC(Component):
    """ An interface to Trac's timeline module.
    """ 
    implements(IXMLRPCHandler)
    sources = ExtensionPoint(ITimelineEventProvider)

    def __init__(self):
#        self._module = TimelineModule(self.env)
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

    # Exported methods
    def getEvents(self, req, start=None, stop=None, filters=None):
        """Return a list of events in the time range given by the 
        `start` and `stop` parameters. Each item is represented as 
        a tuple of the form (kind, author, date, timestamp) 
        containing the data for each event.
        
        The `filters` parameters is a list of the enabled filters, 
        each item being the name of the tuples returned by 
        `ITimelineEventProvider.get_timeline_filters`. If none is 
        specified then all available filters will be used.
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
        STMT = "(kind, author, date, dateuid, " \
                "str(render('url', ctx)), str(render('title', ctx)), " \
                "str(render('description', ctx)))"
        return list(eval(STMT, globs, self._event_data(p, e)) \
                                for p in self.sources \
                                for e in p.get_timeline_events(req, \
                                            start, stop, filters))
    
    def getEventFilters(self, req):
        """Return a list of the filters available to retrieve events 
        provided  by the timeline module. The data returned for each 
        filter is a binary tuple containing the filter name and as 
        well as its display name.
        """
        fdata = dict(fi for p in self.sources \
                        for fi in p.get_timeline_filters(req))
        return fdata.iteritems()

class GVizTimelineEvents(GVizXMLRPCAdapter):
    """Return the timed events contributed to the timeline.
    
    This component depends on tracgviz.timeline.TimelineRPC. The later
    must be enabled. Please read
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
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
    @gviz_param('fmt', "The syntax of both `start` and `stop` fields. "
                            "Here you can embed the directives "
                            "supported by `time.strftime` function. "
                            "The default behavior is to accept the "
                            "well known format `yyyy-mm-dd HH:MM:SS` "
                            "which is actually written like this "
                            "`%Y-%m-%d %H:%M:%S`.")
    @gviz_param('filter', "The name of the filter to be enabled. This "
                            "field may be specified more than once "
                            "in order to select multiple filters.")
    def get_data(self, req, tq, start=None, stop=None, \
                    fmt='%Y-%m-%d %H:%M:%S', filter=None, **tqx):
        """Retrieve ticket actions.
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
    """Return the the available filters provided by the different 
    sources contributing to the timeline.
    
    This component depends on tracgviz.timeline.TimelineRPC. The later
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

