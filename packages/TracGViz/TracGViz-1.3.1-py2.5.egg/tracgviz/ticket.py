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

"""Data sources used to publish the data managed by Trac tickets
system. This includes ticket specific data, and information about 
project milestones, versions, components, and also ticket types, 
status, priority, severity and resolution values.

Note: It relies on Trac XML-RPC plugin.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

from trac.util.datefmt import utc, _epoc
from trac.ticket.roadmap import RoadmapModule, \
                                get_tickets_for_milestone, \
                                apply_ticket_permissions, \
                                get_ticket_stats, milestone_stats_data

from api import gviz_col, gviz_param, GVizBadRequest
from util import GVizXMLRPCAdapter, map_with_id, map_many_with_id, \
                    map_value_with_id

from datetime import datetime
from xmlrpclib import DateTime
from itertools import chain, repeat
import types

#--------------------------------------------------
# Ticket models and enums
#--------------------------------------------------

class GVizModelDataSource(GVizXMLRPCAdapter):
    """Base class for all those data sources exposing Trac resources'
    details with the help of XML RPC handlers following the model 
    adopted in the standard XML RPC implementation. In other words, 
    this data source relies on an XML RPC handler (determined by the
    namespace name returned by `gviz_namespace` method) exporting 
    the following methods :
    
    - getAll : Get a list of all resources names.
    - get : Return a mapping from resource attributes to its value.
      Subclasses may define the proper attribute names and their
      corresponding type by overriding `model_attrs` method.
    """
    abstract = True
    
    def do_init(self):
        attrs = dict(self.model_attrs())
        self._date_attrs = [x for x, v in attrs.iteritems() if v in \
                    ("date", "datetime", "timeofday")]
        self.log.debug("IG: Date attrs for %s are %s", self.__class__, \
                        self._date_attrs)
        self._schema = {('name', 'string') : attrs}
    
    # IGVizDataProvider methods
    def get_data_schema(self):
        return self._schema
    
    def _clean_dates(self, result):
        """This function cleans the mess created by Trac RPC handlers
        returning `0` instead of `None` due to XML-RPC limitations.
        
        @param result the object to be returned to the caller.
        """
        for item in result.itervalues():
            for attr in self._date_attrs:
                if item[attr] == 0:
                    item[attr] = None
    
    def get_data(self, req, tq, **tqx):
        """Get the models' data.
        
        @return the data associated with the resources. Query 
                string and parameters are ignored.
        """
        obj = self._rpc_obj
        result = dict([n, obj.get(req, n)] for n in obj.getAll(req))
        if self._date_attrs:
            self._clean_dates(result)
        return result
    
    def model_attrs(self):
        """This method is provided so that subclasses be able to 
        specify the model attributes included in a Data Table object.
        If not overriden then it raises `NotImplementedError` since
        this highlights an error in a data provider's implementation.
        
        @return a dictionary, a sequence of binary tuples, or any 
                other compatible object, mapping the different
                attribute names to their corresponding type.
        """
        raise NotImplementedError('Unspecified model attributes in'
                'data provider %s' % ('/'.join(self.gviz_namespace()),))

import trac.ticket.model as model

def gvizTicketModelFactory(cls, attrs):
    """Create very quickly a model-based data source (ticket models).
    
    @param cls the model class (e.g. `trac.ticket.model.Component`).
    @param attrs the model attributes specified by a sequence of
                (name, type) tuples.
    """
    class GVizTicketModelImpl(GVizModelDataSource):
        abstract = False
        def gviz_namespace(self):
            return ('ticket', cls.__name__.lower())
        
        @gviz_col('name', "The display name given to the %s." % \
                                            (cls.__name__.lower(),))
        def get_data(self, req, tq, **tqx):
            return GVizModelDataSource.get_data(self, req, tq, **tqx)
        for nm,v in attrs.iteritems():
            desc = "The %s %s" % (cls.__name__.lower(), nm)
            if v == 'datetime' and nm != 'time':
                desc+= ' time'
            get_data = gviz_col(nm, desc)(get_data)
        del desc, nm, v
        
        def model_attrs(self):
            return attrs
    
    GVizTicketModelImpl.__doc__ = "GViz provider to ticket %s objects. " \
            "This component depends on tracrpc.ticket.%sRPC. " \
            "The later must be enabled. Read " \
            "https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/" \
            "TracGViz/DataSources#Preconditions" % \
                    (cls.__name__.lower(), cls.__name__)
    GVizTicketModelImpl.__name__ = 'GViz%sProvider' % cls.__name__
    return GVizTicketModelImpl

def gvizEnumFactory(cls):
    """Create very quickly an enum-based data source (ticket 
    attributes).
    
    @param cls the enum class (e.g. `trac.ticket.model.Status`).
    """
    class GVizTicketEnumImpl(GVizModelDataSource):
        abstract = False
        def gviz_namespace(self):
            return ('ticket', cls.__name__.lower())
        def do_init(self):
            self._date_attrs = None
        
        @gviz_col('name', "The display name of the ticket %s value." % \
                                            (cls.__name__.lower(),))
        @gviz_col('value', "The value identifying the ticket %s." % \
                                            (cls.__name__.lower(),))
        def get_data(self, req, tq, **tqx):
            return GVizModelDataSource.get_data(self, req, tq, **tqx)
        
        def get_data_schema(self):
            return {('name', 'string') : ('value', 'string')}
    
    GVizTicketEnumImpl.__doc__ = "GViz provider to ticket %s objects." \
            "This component depends on tracrpc.ticket.%sRPC. " \
            "The later must be enabled. Read " \
            "https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/" \
            "TracGViz/DataSources#Preconditions" % \
                    (cls.__name__.lower(), cls.__name__)
    GVizTicketEnumImpl.__name__ = 'GViz%sProvider' % cls.__name__
    return GVizTicketEnumImpl

gvizTicketModelFactory(model.Component, 
        {'owner': 'string', 'description': 'string'})
gvizTicketModelFactory(model.Version, 
        {'time': 'datetime', 'description': 'string'})

gvizEnumFactory(model.Type)
gvizEnumFactory(model.Status)
gvizEnumFactory(model.Resolution)
gvizEnumFactory(model.Priority)
gvizEnumFactory(model.Severity)

# In this case I want to expose much more data.
#
# gvizTicketModelFactory(model.Milestone, 
#        {'due': 'datetime', 'completed': 'datetime', \
#                'description': 'string'})

def mstats(env, mname, req, stats_provider):
    """ Return a summary of the tickets bound to a milestone.
    
    @param env : the Trac environment
    @param mname : the name of the milestone
    @param req : an object encapsulating the request made by the client
    """
    tickets = get_tickets_for_milestone(env, env.get_db_cnx(), \
                                        mname, 'owner')
    tickets = apply_ticket_permissions(env, req, tickets)
    stat = get_ticket_stats(stats_provider, tickets)
    
    # FIXME : Efficency
    istats = dict([i['title'], [i['count'], i['percent']]] \
                        for i in stat.intervals)
    return [stat.done_count, stat.count, stat.unit, stat.done_percent] + \
                istats.get('active', [None, None]) + \
                istats.get('closed', [None, None])

class GVizMilestoneProvider(GVizModelDataSource):
    """Data source providing data related to project milestones 
    (including progress, and other metadata). This component depends on 
    tracrpc.ticket.%sRPC. The later must be enabled. Please read 
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    abstract = False
    def gviz_namespace(self):
        return ('ticket', 'milestone')
    
    # IGVizDataProvider methods
    def get_data_schema(self):
        return [
                # Milestone attributes
                ('name', 'string'), ('due', 'datetime'), \
                ('completed', 'datetime'), ('description', 'string'), \
                # Stats
                ('done', 'number'), ('total', 'number'), \
                ('unit', 'string'), ('percent', 'number'), \
                ('active_count', 'number'), ('active_percent', 'number'),
                ('closed_count', 'number'), ('closed_percent', 'number') \
                ]
    
    @gviz_col('name', "The milestone display name.")
    @gviz_col('due', "The due time for this milestone.")
    @gviz_col('completed', "The instant when this milestone was "
                            "attained.")
    @gviz_col('description', "Full description for this milestone.")
    @gviz_col('done', "The amount of work that's been done.")
    @gviz_col('unit', "The display name of the units used to measure "
                        "the indicators reflecting the progress "
                        "towards each milestone.")
    @gviz_col('percent', "Percent of the whole work that's been "
                            "already done.")
    @gviz_col('total', "The total amount of work that needs to be "
                        "done in order to achieve each milestone.")
    @gviz_col('active_count', "The number of active tickets (if measured).")
    @gviz_col('active_percent', "The percent that represents the number "
                                "of active tickets with respect to "
                                "the total amount of tickets "
                                "(if measured).")
    @gviz_col('closed_count', "The number of closed tickets (if measured).")
    @gviz_col('closed_percent', "The percent that represents the number "
                                "of closed tickets with respect to "
                                "the total amount of tickets "
                                "(if measured).")
    def get_data(self, req, tq, **tqx):
        """Insert milestone stats.
        """
        env = self.env
        sp = RoadmapModule(env).stats_provider
        BaseClass = GVizModelDataSource
        return ([nm] + [attrs[k] for k in ('due', 'completed', 'description')] + \
                mstats(env, nm, req, sp) for nm, attrs in \
                    BaseClass.get_data(self, req, tq, **tqx).iteritems())
    
    def model_attrs(self):
        return {'due': 'datetime', 'completed': 'datetime', \
                'description': 'string'}

#--------------------------------------------------
# Tickets meta-data
#--------------------------------------------------

class BaseTicketResultSet(GVizXMLRPCAdapter):
    abstract = True
    def _retrieve_tickets(self, req, ids=None, since=None):
        """Parse the tickets supplied in to `ids` parameter. If none 
        is specified then return all the tickets modified since a 
        given timestamp (defaults to the epoch).
        """
        try:
            if ids is not None:
                if isinstance(ids, types.StringTypes):
                    return (int(ids),)
                else:
                    return dict([int(x), None] for x in ids).iterkeys()
            elif since is not None:
                return self._rpc_obj.getRecentChanges(req, since)
            else:
                return self._rpc_obj.getRecentChanges( \
                            req, DateTime(_epoc))
        except ValueError, exc:
            raise GVizBadRequest("Invalid ticket id : %s" % (exc.message,))
    
    from util import convert_req_date as _convert_date
    _convert_date = staticmethod(_convert_date)
    
class GVizTicketActions(BaseTicketResultSet):
    """Returns the actions that can be performed on tickets.
    
    This component depends on tracrpc.ticket.TicketRPC. The later 
    must be enabled. Please read 
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    # IGVizDataProvider methods
    def get_data_schema(self):
        return [('id', 'number'), \
                ('name', 'string', 'Action name')]
    
    @gviz_col('id', "The id of the ticket for which the action is "
                    "available.")
    @gviz_col('name', "The name of the action supported by the ticket")
    @gviz_param('id', "Ticket id (mandatory field). If missing "
                        "then an error is sent back to the caller")
    def get_data(self, req, tq, id=None, **tqx):
        """Retrieve ticket actions.
        """
        ids = self._retrieve_tickets(req, id, since=None)
        return map_value_with_id(req, (int(x) for x in ids), \
                            self._rpc_obj.getAvailableActions)
    
    def xmlrpc_namespace(self):
        """Use Ticket XML-RPC.
        """
        return ('ticket',)
    def gviz_namespace(self):
        return ('ticket', 'actions')

class GVizTicketFields(GVizXMLRPCAdapter):
    """Return a list of all ticket fields. 
    
    Important: The order of the columns can change from time to time.
    
    This component depends on tracrpc.ticket.TicketRPC. The later 
    must be enabled. Please read 
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    # IGVizDataProvider methods
    def get_data_schema(self):
        return {'name' : 'string', 'label' : 'string', \
                'type' : 'string', 'options' : 'string', \
                'value' : 'string', 'optional' : 'boolean'}
    
    @gviz_col('name', "Field name.")
    @gviz_col('label', "Field's display name.")
    @gviz_col('type', "The kind of field (e.g. `radio`, `text`, "
                        "`textarea`).")
    @gviz_col('options', "Available options for this field (e.g. "
                        "in case of being a `radio` field). The "
                        "values are encoded in a single string. You "
                        "could supply that value in to `eval` fuction "
                        "in order to obtain the options list. "
                        "However the same data could be provided by "
                        "another data source.")
    @gviz_col('value', "Default value e.g. in case of being a "
                        "`radio` field).")
    @gviz_col('optional', "Whether this field is optional or not.")
    def get_data(self, req, tq, **tqx):
        """Retrieve ticket actions.
        """
        result = self._rpc_obj.getTicketFields(req)
        for f in result:
            for k,v in f.iteritems():
                if k == 'options':
                    f['options'] = [o.encode('utf-8', 'replace') \
                                    for o in v]
        return result
    
    def xmlrpc_namespace(self):
        """Use Ticket XML-RPC.
        """
        return ('ticket',)
    def gviz_namespace(self):
        return ('ticket', 'fields')

#--------------------------------------------------
# Information consisting of groups of tickets 
#--------------------------------------------------



#--------------------------------------------------
# Miscellaneous
#--------------------------------------------------

class GVizTicketChangeLog(BaseTicketResultSet):
    """Return the changelog as a datatable. Please read the 
    specification for further details about the parameters and 
    columns involved.
    
    This component depends on tracrpc.ticket.TicketRPC. The later 
    must be enabled. Please read 
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    # IGVizDataProvider methods
    def get_data_schema(self):
        return [('id', 'number'), ('time', 'datetime'), 
                ('author' , 'string'), \
                ('field' , 'string'), ('oldvalue' , 'string'), \
                ('newvalue' , 'string'), ('permanent' , 'boolean')]
    
    @gviz_col('id', "The id of the ticket being modified.")
    @gviz_col('time', "The moment when the change took place.")
    @gviz_col('author', "The user that was performing this change.")
    @gviz_col('field', "The ticket field that was modified.")
    @gviz_col('oldvalue', "The value of the affected field before "
                        "the change took place.")
    @gviz_col('newvalue', "The value assigned to the target field.")
    @gviz_col('permanent', "While the other elements are quite "
                            "self-explanatory, the permanent flag "
                            "is used to distinguish collateral "
                            "changes that are not yet immutable "
                            "(like attachments, currently).")
    @gviz_param('id', "The id of the tickets whose changes are to be "
                        "requested. You can specify this parameter "
                        "multiple times in order to specify multiple "
                        "tickets at once. If not specified then only "
                        "those tickets having modifications in the "
                        "selected time window will be the ones listed.")
    @gviz_param('at', "Show changes made at this moment (UTC). Can "
                        "be specified more than once. "
                        "If both `at` and `since` fields are missing "
                        "then the full changelog will be returned.")
    @gviz_param('since', "Show *ALL* the modifications made on "
                            "tickets that have changed since "
                            "timestamp (UTC). Should be specified "
                            "only once. If both `at` and `since` "
                            "fields are missing then the full "
                            "changelog will be returned.")
    @gviz_param('fmt', "The syntax of `when` field. Here you "
                            "can embed the directives supported by "
                            "`time.strftime` function. The default "
                            "behavior is to accept the well known "
                            "format `yyyy-mm-dd HH:MM:SS` which is "
                            "actually written like this "
                            "`%Y-%m-%d %H:%M:%S`.")
    def get_data(self, req, tq, id=None, at=None, since=None,
                    fmt='%Y-%m-%d %H:%M:%S', **tqx):
        """Retrieve the changes performed on tickets.
        """
        self.log.debug("IG: Since date %s", since)
        self.log.debug("IG: At date %s", at)
        try:
            if isinstance(at, types.StringTypes):
                at = [self._convert_date(at, fmt, req)]
            elif at is not None:
                at = (self._convert_date(t, fmt, req) for t in at)
            if since is not None:
                since = self._convert_date(since, fmt, req)
                if at is not None:
                    at = (t for t in at if  t < since)
        except:
            raise GVizBadRequest("Invalid datetime value")
        
        ids = self._retrieve_tickets(req, id, since)
        self.log.debug('Modified tickets ids %s', ids)
        
        if at is not None:
            result = chain(*(map_many_with_id(req, ids, \
                    self._rpc_obj.changeLog, repeat(t)) for t in at))
        else:
            result = ()
        if since is None and at is None:
            since = DateTime(_epoc)
        self.log.debug("IG: Since date %s", since)
        if since is not None:
#            since = DateTime(since)
            def cmp_dates(dt, snc):
                self.log.debug('Comparing %s and %s yields %s', dt, snc, dt >= snc)
                return 
            result = chain(result, (x for x in \
                    map_many_with_id(req, ids, self._rpc_obj.changeLog) \
                    if x[1] >= since))
        return result
    
    def xmlrpc_namespace(self):
        """Use Ticket XML-RPC.
        """
        return ('ticket',)
    def gviz_namespace(self):
        return ('ticket', 'log')

class GVizTicketAttachments(BaseTicketResultSet):
    """Return ticket attachments as a datatable. Please read the 
    specification for further details about the parameters and 
    the columns returned.
    
    This component depends on tracrpc.ticket.TicketRPC. The later 
    must be enabled. Please read 
    https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/TracGViz/DataSources#Preconditions
    for further details.
    """
    # IGVizDataProvider methods
    def get_data_schema(self):
        return [('id', 'number'), ('url' , 'string'), \
                ('filename' , 'string'), \
                ('description' , 'string'), ('size' , 'number'), \
                ('date', 'datetime'), ('author' , 'string')]
    
    @gviz_col('id', "The ticket id.")
    @gviz_col('url', "The attachment's URL.")
    @gviz_col('filename', "Filename.")
    @gviz_col('author', "The user that uploaded the file.")
    @gviz_col('description', "An text highlighting the contents of "
                            "the file.")
    @gviz_col('size', "The size of the attachment (in bytes).")
    @gviz_col('date', "The time when the file was submitted onto "
                        "the server.")
    @gviz_param('id', "The id of the ticket whose attachments are "
                        "to be retrieved.")
    def get_data(self, req, tq, id=None, **tqx):
        """Retrieve the tickets' attachments.
        """
        ids = self._retrieve_tickets(req, id, since=None)
        def listAttachments(req, id):
            return ((req.abs_href('attachment/ticket', id, x[0]),) + x \
                   for x in self._rpc_obj.listAttachments(req, id))
        return map_many_with_id(req, ids, listAttachments)
    
    def xmlrpc_namespace(self):
        """Use Ticket XML-RPC.
        """
        return ('ticket',)
    def gviz_namespace(self):
        return ('ticket', 'attachments')


