#!/usr/bin/env python

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

r"""Basic features needed to support Google Visualization Query Language
(aka. GVizQL).

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

__all__ = 'prepare_ql_data', 'GVizQLClauseHandler', 'GVizQLParser', \
          'defaultParser'
__metaclass__ = type

from re import compile

#------------------------------------------------------
#   GVizQL parsing and compilation
#------------------------------------------------------

class GVizQLParser:
  r"""Objects used to parse GVizQL expressions. 
  """
  GVIZ_QL_RE = None
  GVIZ_QL_TOKENS = {
        'id' : '(?:[a-zA-Z]\w*|' # Simple identifiers \
                  '`(?:\w|\s)*`)'   # Identifiers enclosed in backquotes,
      }
  updated = False
  
  @property
  def pattern(self):
    r"""Retrieve the regular expression describing the whole GVizQL 
    syntax.
    """
    if not self.__class__.updated:
      self.update_syntax()
      self.__class__.updated = True
    return self.GVIZ_QL_RE
  @classmethod
  def update_syntax(cls):
    r"""Update the regular expression describing the whole GVizQL 
    syntax.
    """
    patt = '\s*%s\s*$' % '(?:\s+|$|^)'.join( '(?:%s)?' %
                                (ct.SYNTAX % cls.GVIZ_QL_TOKENS) \
                                for ct in GVizQLClauseType.iterparse() \
                                if ct.SYNTAX)
    cls.GVIZ_QL_RE = compile(patt)
  
  def parse(self, tq):
    r"""Parse and compile a GVizQL expression.
    """
    mo = self.pattern.match(tq)
    if mo:
      return GVizQLExpression(mo)
    else:
      return

defaultParser = GVizQLParser()

class GVizQLExpression:
  r"""Compiled GVizQL expression.
  """
  def __init__(self, mo):
    r"""Initialize a compiled GVizQL expression. 
    
    @param mo       the match made by the parser.
    """
    self.mo = mo

#------------------------------------------------------
#   GVizQL clause handlers 
#------------------------------------------------------

class GVizQLClauseType(type):
  r"""Keep track of all GVizQL clause handlers installed in the 
  system, as well as evaluation order.
  
  >>> ','.join(ct.get_props('keyw') for ct in GVizQLClauseType.iterparse())
  'select,from,where,group by,pivot,order by,limit,offset,label,format,options'
  >>> ','.join(ct.get_props('keyw') for ct in GVizQLClauseType.itereval())
  'from,group by,pivot,where,order by,offset,limit,select,format,options,label'
  """
  CLAUSE_CACHE = dict()
  SYNTAX_ORDER = list()
  EVAL_ORDER = list()
  PROPS = ('idx_syntax', 'idx_eval', 'keyw')
  
  def __new__(cls, name, bases, suite):
    r"""Keep track of all GVizQL clause handlers installed in the 
    system, as well as evaluation order.
    """
    try:
      abstract = suite['__abstract__']
      del suite['__abstract__']
    except KeyError:
      abstract = False
    
    @classmethod
    def get_props(cls, propnm):
      try:
        return self._PROPS[propnm]
      except KeyError, exc:
        raise ValueError('Unsupported property %s', exc.message)
    suite['get_props'] = get_props
    
    self = super(GVizQLClauseType, cls).__new__(cls, name, bases, suite)
    if not abstract:
      cnm = self.get_props('keyw')
      GVizQLClauseType.CLAUSE_CACHE[cnm] = self
      GVizQLClauseType.SYNTAX_ORDER.append(self)
      GVizQLClauseType.SYNTAX_ORDER.sort(None, \
                                    lambda x: x.get_props('idx_syntax'))
      GVizQLClauseType.EVAL_ORDER.append(self)
      GVizQLClauseType.EVAL_ORDER.sort(None, \
                                    lambda x: x.get_props('idx_eval'))
    GVizQLParser.updated = False
    return self
  
  @staticmethod
  def itereval():
    r"""Iterate over GVizQL clause handlers following evaluation order.
    """
    return iter(GVizQLClauseType.EVAL_ORDER)
  
  @staticmethod
  def iterparse():
    r"""Iterate over GVizQL clause handlers following syntax order.
    """
    return iter(GVizQLClauseType.SYNTAX_ORDER)

class GVizQLClauseHandler:
  r"""Objects used to parse and retrieve items inside a clause and 
  also responsible of performing the transformations dictated by this 
  clause.
  """
  __metaclass__ = GVizQLClauseType
  __abstract__ = True

class GVizSelectClause(GVizQLClauseHandler):
  _PROPS = {'idx_syntax' : 0, 'idx_eval': 7, 'keyw' : 'select'}
  # TODO: Add more complex expressions
  SYNTAX = r'select\ (?:\*|(?P<cols>%(id)s(?:,\s*%(id)s)*))'

class GVizFromClause(GVizQLClauseHandler):
  _PROPS = {'idx_syntax' : 1, 'idx_eval': 0, 'keyw' : 'from'}
  SYNTAX = r'from\ (?P<basetable>%(id)s)'

class GVizWhereClause(GVizQLClauseHandler):
  _PROPS = {'idx_syntax' : 2, 'idx_eval': 3, 'keyw' : 'where'}
  SYNTAX = r'where\ .*\s(?:%s)' % \
              ('|'.join(GVizQLClauseType.CLAUSE_CACHE.keys()))

class GVizGroupByClause(GVizQLClauseHandler):
  _PROPS = {'idx_syntax' : 3, 'idx_eval': 1, 'keyw' : 'group by'}
  SYNTAX = r''

class GVizPivotClause(GVizQLClauseHandler):
  _PROPS = {'idx_syntax' : 4, 'idx_eval': 2, 'keyw' : 'pivot'}
  SYNTAX = r''

class GVizOrderByClause(GVizQLClauseHandler):
  _PROPS = {'idx_syntax' : 5, 'idx_eval': 4, 'keyw' : 'order by'}
  SYNTAX = r''

class GVizLimitClause(GVizQLClauseHandler):
  _PROPS = {'idx_syntax' : 6, 'idx_eval': 6, 'keyw' : 'limit'}
  SYNTAX = r''

class GVizOffsetClause(GVizQLClauseHandler):
  _PROPS = {'idx_syntax' : 7, 'idx_eval': 5, 'keyw' : 'offset'}
  SYNTAX = r''

class GVizLabelClause(GVizQLClauseHandler):
  _PROPS = {'idx_syntax' : 8, 'idx_eval': 10, 'keyw' : 'label'}
  SYNTAX = r''

class GVizFormatClause(GVizQLClauseHandler):
  _PROPS = {'idx_syntax' : 9, 'idx_eval': 8, 'keyw' : 'format'}
  SYNTAX = r''

class GVizOptionsClause(GVizQLClauseHandler):
  _PROPS = {'idx_syntax' : 10, 'idx_eval': 9, 'keyw' : 'options'}
  SYNTAX = r''

#------------------------------------------------------
#   Helper functions
#------------------------------------------------------

def prepare_ql_data(provider, tq, req, **params):
  r"""Prepare the data and schema to be supplied to an instance of 
  gviz_api.DataTable as determined by a GVizQL expression. This is 
  accomplished by wrapping the original data with multiple iterators.
  
  @param provider   an instance of `IGVizDataProvider` interface 
                    responsible for providing the base result set 
                    (i.e. primary information) subsequently modified 
                    by the application of the GVizQL expression.
  @param tq         the GVizQL expression.
  @param req        an object encapsulating the HTTP request/response 
                    pair.
  @param params     further parameters supported by `provider`.
  @return           a binary tuple. The first item is the schema 
                    describing the column names, data types, and 
                    labels, as well as data structures from where 
                    data will be retrieved. The second is the actual 
                    data resulting from the application of the query 
                    (quite often in the form of iterators).
  """
  sch = provider.get_data_schema.im_func.func_code
  sch_args = (sch.co_argcount > 1) and (req,) or ()
  if not tq:
    data = provider.get_data(req, None, **params)
    return (provider.get_data_schema(*sch_args), data)
  else:
    tq = defaultParser.parse(tq)
    data = provider.get_data(req, tq, **params)
    sch = provider.get_data_schema(*sch_args)
    return tq.transform(sch, data, req)

#------------------------------------------------------
#   Global Testing
#------------------------------------------------------

__test__ = {
  'Parser setup' : r"""
      # >>> defaultParser.pattern.pattern
      """,
  'Parsing SELECT (simple)' : r"""
      >>> defaultParser.parse('  select *  ')
      <...GVizQLExpression object at ...>
      >>> defaultParser.parse('select dept, salary  ')
      <...GVizQLExpression object at ...>
      >>> defaultParser.parse('select `email address`, name, `date`')
      <...GVizQLExpression object at ...>
      >>> defaultParser.parse('select lunchTime, name')
      <...GVizQLExpression object at ...>
      """,
  'Parsing SELECT (complex)' : r"""
      #>>> defaultParser.parse('select max(salary)')
      #<...GVizQLExpression object at ...>
      """,
  'Parsing FROM (simple)' : r"""
      >>> defaultParser.parse('  from employees') 
      <...GVizQLExpression object at ...>
      >>> defaultParser.parse('from `employees`')
      <...GVizQLExpression object at ...>
      >>> defaultParser.parse('select dept, salary from emp_data')
      <...GVizQLExpression object at ...>
      """,
  }

def test_suite():
  from testing.dutest import MultiTestLoader, DocTestLoader
  from unittest import defaultTestLoader
  from doctest import ELLIPSIS
  import sys
  l = MultiTestLoader([defaultTestLoader, \
                        DocTestLoader(
                            extraglobs=dict(parse=defaultParser.parse),
                            optionflags=ELLIPSIS
                          )])
  return l.loadTestsFromModule(sys.modules[__name__])

