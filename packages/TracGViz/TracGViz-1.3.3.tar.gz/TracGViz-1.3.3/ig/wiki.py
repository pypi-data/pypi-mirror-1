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

r"""This module contains all the elements available to embed gadgets 
and visualizations everywhere WikiFormatting is supported. This
includes both macros and processors. However some other elements 
aiming at similar purposes will be coded in separate modules in case
the logic behind the specific macro or processor be strongly coupled
with other component elements.
"""

__all__ = 'iGoogleGadgetMacro', 'GoogleVizGadgets', 'GadgetAliases'

from trac.core import Component, implements, TracError
from trac.config import ListOption
from trac.env import Environment
from trac.mimeview.api import Context
from trac.wiki.api import parse_args, IWikiMacroProvider
from trac.wiki.formatter import Formatter
from trac.wiki.macros import WikiMacroBase

from genshi.core import Markup
from genshi.builder import Element

from itertools import chain
from urlparse import urlunparse
from urllib import urlencode

from tracgviz.api import ITracLinksHandler
from tracgviz.util import dummy_request

__metaclass__ = type

class TracLinksFormatter(Formatter):
    r"""A wiki formatter which pays attention to nothing but trac 
    links.
    """
    for fmt_name in (x for x in Formatter.__dict__ \
            if x.endswith('_formatter') and \
            x not in ['_lhref_formatter', '_shref_formatter']):
        locals()[fmt_name] = lambda *args, **kwds: ''
    del fmt_name

class FirstTracLinkFormatter(TracLinksFormatter):
    r"""Gather the first TracLink found.
    """
    def __init__(self, env, context):
        super(FirstTracLinkFormatter, self).__init__(env, context)
        self._first_link = None
    
    def _lhref_formatter(self, match, fullmatch):
        link = super(FirstTracLinkFormatter, self)._lhref_formatter(match, fullmatch)
        self.env.log.debug("GVIZ: LinkFormatter LHREF rule triggered. "
                        "Match= '%s' Full match= '%s' Link= '%s'", 
                        match, fullmatch, link)
        if not self._first_link:
            self._first_link = link
        return link
        
    def _shref_formatter(self, match, fullmatch):
        link = super(FirstTracLinkFormatter, self)._shref_formatter(match, fullmatch)
        self.env.log.debug("GVIZ: LinkFormatter SHREF rule triggered. "
                        "Match= '%s' Full match= '%s' Link= '%s'", 
                        match, fullmatch, link)
        if not self._first_link:
            self._first_link = link
        return link
    
    def extract_link(self, lnk_obj):
        raise TracError('Unable to extract TracLink from DOM object.')
    
    @property
    def first_link(self):
        link = self._first_link
        if not link:
            return None
        elif isinstance(link, Element):
            return link.attrib.get('href')
        else:
            return self.extract_link(link)
    
class iGoogleGadgetMacro(WikiMacroBase):
    r"""A quick and easy way to embed iGoogle gadgets in your wiki 
    pages.
    
    This macro accepts the following parameters:
     - `url` : The location where the gadget XML specification can be 
       found. This parameter supports TracLinks expansion (see below).
     - `title` : The title shown on top of the gadget. If you blank 
       out this field, the effect in the deployed gadget is that the 
       border is clean and there is no title bar. This is the default 
       behavior if `title` is not explicitly set. This field accepts
       [http://code.google.com/apis/gadgets/docs/legacy/gs.html#UP_MP substitution variables].
     - `height` and `width` parameters : The value of these 
       parameters is typically the number of pixels. However, you can 
       set the gadget width to fill the containing space by using 
       `width=auto`. This is useful for flexible layouts where you don't 
       know the number of pixels beforehand. The default values are 
       `320` for width and `200` for height.
     - `border` : String used to specify the border that you want to 
       display around your gadget on the target web page. This field 
       supports TracLinks expansion (see below) to specify the URL 
       for an image-based gadget border.
     - `output` : Indicates how the syndicated 
       gadget is rendered. Possible values are `js` for JavaScript if 
       the gadget uses '''<script>''' tags, and `html` for everything 
       else.  Most of the time you should not be concerned about 
       setting this field. Default value is `js`.
     - `lang` : Some gadgets support localization (i.e. the 
       [http://gmodules.com/ig/creator?synd=open&url=http://doc.examples.googlepages.com/baseball-card.xml creator page] 
       includes a Language menu that contains all the languages 
       supported by your gadget according to the `<Locale>` elements 
       found in the gadget descriptor). If this is the case, you can 
       specify the a string identifying the locale you want to use to
       display your gadget (e.g. default value is `en_US`).
     - `country` : The country value used for internalization (see
       [http://code.google.com/apis/gadgets/docs/legacy/i18n.html Gadget i18n reference]). 
       Its default setting is `ALL`
    
    The parameters supporting TracLinks expansion, accept any TracLinks
    expression. If the target URL cannot be reached, the macro fails
    to expand and an exception is raised.
    """
    # TODO: Move off
    @staticmethod
    def resolve_link_url(formatter, link_text):
        r"""Resolve a TracLinks expression.
        
        @param link_text the TracLinks expression.
        @return the location (i.e. URL) this link is pointing to.
        """
        # FIXED: Generate absoulte links
        # req, env, ctx = formatter.req, formatter.env, formatter.context
        if isinstance(formatter, Environment):
          env = formatter
          req = dummy_request(env)
        else:
          req, env = formatter.req, formatter.env
        ctx = Context.from_request(req, absurls=True)
        abs_ref, href = (req or env).abs_href, (req or env).href
        lf = FirstTracLinkFormatter(env, ctx)
        lf.format(link_text)
        return lf.first_link
    
    MACRO_DEFAULTS = dict(
            title='', width=320, height=200, output='js',
            lang='en_US', country='ALL',
            border=r"#ffffff|1px,1px solid black|1px,1px" \
                        " solid black|0px,1px black"
            )
    
    def do_expand_macro(self, formatter, args):
        r"""Return the script tag needed to embed the iGoogle gadget 
        considering the arguments supplied in the call to the macro.
        """
        url = self.resolve_link_url(formatter, args.get('url', ''))
        if not url:
            raise TracError("Unknown gadget : 'url' argument " \
                            "is either wrong or missing")
        del args['url']
        defaults = self.MACRO_DEFAULTS
        spec_args = dict([arg, args.pop(arg, defval)] 
                        for arg, defval in defaults.iteritems())
        spec_args['w'] = spec_args.pop('width')
        spec_args['h'] = spec_args.pop('height')
        border = self.resolve_link_url(formatter, spec_args['border'])
        if border:
            spec_args['border'] = border
        gadget_params = dict(chain([('url', url), ('synd', 'open')], \
                (['up_' + k, \
                 (v.startswith('[') and v.endswith(']')) and \
                        self.resolve_link_url(formatter, v) or v] \
                        for k, v in args.iteritems()), # custom args ;)
                spec_args.iteritems()))
        url = urlunparse(['http', 'gmodules.com', '/ig/ifr', '', \
                        urlencode(gadget_params), ''])
        
        self.log.debug("IG: Gadget preferences %s", gadget_params)
        return Markup('<script src="%s"></script>' % (url,))
    
    def expand_macro(self, formatter, name, contents):
        r"""Expand iGoogleGadget macro.
        """
        _, args = parse_args(contents)
        self.log.debug('IG: iGoogleGadgetMacro -> args = %s', args)
        return self.do_expand_macro(formatter, args)

GOOGLE_MODULES_URL = 'http://www.google.com/ig/modules/%s.xml'

class GoogleVizGadgets(Component):
    r"""Provide shortcuts based on WikiFormatting so as to specify 
    URLs for (standard) Google Visualization Gadgets.
    
    Syntax -> 
    gadget:google:modules:<chart_name>
    
    Example(s) ->
    - gadget:google:modules:line-chart
      http://www.google.com/ig/modules/line-chart.xml
    """
    implements(ITracLinksHandler)
    
    # ITracLinksHandler methods
    def _format_link(self, formatter, ns, viz_name, label):
        title = "Google's Official Visualization: %s" % (viz_name,)
        url = GOOGLE_MODULES_URL % (viz_name,)
        return formatter._make_ext_link(url, label, title)
    
    def get_link_resolvers(self):
        r"""Return an iterable over (namespace, formatter) tuples.

        Each formatter should be a function of the form
        fmt(formatter, ns, target, label), and should
        return some HTML fragment.
        The `label` is already HTML escaped, whereas the `target` is not.
        """
        yield (('gadget', 'google', 'modules'), self._format_link)

class GadgetAliases(Component):
  r"""A class allowing to write aliases for favorite gadgets to be 
  embedded in wiki pages, so it's quite easy to remember how to 
  embed it. For further details read the documentation for option 
  `gadgets.aliases`.
  """
  implements(IWikiMacroProvider)
  
  GOOGLE_GADGETS = [
                      ('MotionChart',       'motionchart'),
                      ('GeoMap',            'geomap'),
                      ('AnnotatedTimeLine', 'time-series-line'),
                      ('Sparkline',         'image-sparkline'),
                      ('Gauge',             'gauge'),
                      ('AreaChart',         'area-chart'),
                      ('ImageAreaChart',    'image-area-chart'),
                      ('BarChart',          'bar-chart'),
                      ('ColumnChart',       'column-chart'),
                      ('LineChart',         'line-chart'),
                      ('PieChart',          'pie-chart'),
                      ('ScatterChart',      'scatter-chart'),
                      ('ImageBarChart',     'image-bar-chart'),
                      ('ImageLineChart',    'image-line-chart'),
                      ('ImagePieChart',     'image-pie-chart'),
                      ('SimpleTable',       'simple-table'),
                      ('SpreadsheetTable',  'table'),
                      ('IntensityMap',      'heatmap'),
                      ('Map',               'map'),
                      ('OrgChart',          'orgchart'),
                      ('WebSearch',         'web-search'),
                      ('ImageSearch',       'image-search'),
                    ]
  aliases = ListOption('gadgets', 'aliases', \
              default=','.join('='.join([nm, GOOGLE_MODULES_URL % (gvid,)]) \
                                for nm, gvid in GOOGLE_GADGETS), \
              keep_empty=False,
              doc="""A comma separated list of macro name followed """
                  """by one gadget URL. Both values are separated """
                  """using the equal sign (=). If a macro with this """
                  """name is written anywhere WikiFormatting is """
                  """accepted then the gadget hosted at URL will be """
                  """embedded (e.g. `[[MotionChart(...)]]` is """
                  """actually equivalent to """
                  """`[[iGoogleGadget(http://www.google.com/ig/"""
                  """modules/motionchart.xml, ...)]]` provided that """
                  """`MotionChart=http://www.google.com/ig/"""
                  """modules/motionchart.xml` be included in this """
                  """option).""")
  
  def __init__(self):
    try:
      self.base_macro = iGoogleGadgetMacro(self.env)
    except:
      self.log.exception("Error loading iGoogleGadgetMacro. Is it enabled?")
      raise TracError("Error loading iGoogleGadgetMacro. Is it enabled?")
    try:
      def cfg(nm, val):
        return nm.strip(), \
                self.base_macro.resolve_link_url(self.env, val.strip())
      
      self.macro_map = dict(cfg(*x.split('=', 1)) for x in self.aliases)
    except:
      self.log.exception("Invalid value in option gadgets.aliases")
#      raise TracError("Invalid value in option gadgets.aliases")
      raise ValueError("Full Value: %s " % (self.aliases,))
  
  # IWikiMacroProvider methods
  def get_macros(self):
      r"""Return the macro names configured in `gadgets.aliases`.
      """
      return self.macro_map.iterkeys()
  
  MACRO_DESC = r"""%(macro)s macro is a shorcut used to embed the 
      gadget hosted at %(url)s. In this case the following wiki 
      expressions are equivalent.
      
      {{{
      [[%(macro)s(arg1=value1,arg2=value2)]]
      [[iGoogleGadget(url=%(url)s,arg1=value1,arg2=value2)]]
      }}}
      """
  
  def get_macro_description(self, name):
      r"""Return a description of the macro with the specified name.
      """
      try:
        url = self.macro_map[name]
      except KeyError:
        return ""
      else:
        return self.MACRO_DESC % dict(macro=name, url=url)
  
  def render_macro(self, req, name, content):
      """Deprecated."""
      raise NotImplementedError("Only Trac>=0.11 is supported")
  
  def expand_macro(self, formatter, name, content):
      r"""Called by the formatter when rendering the parsed wiki text.

      (since 0.11)
      """
      try:
        url = self.macro_map[name]
      except KeyError:
        raise TracError("Unknown alias for iGoogleGadget '%s'" % (name,))
      else:
        _, args = parse_args(content)
        try:
          _ = args['url']
          raise TracError("Argument 'url' cannot be specified.")
        except KeyError:
          args['url'] = url
          return self.base_macro.do_expand_macro(formatter, args)
