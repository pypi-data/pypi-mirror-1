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

"""This module contains all the elements available to embed gadgets 
and visualizations everywhere WikiFormatting is supported. This
includes both macros and processors. However some other elements 
aiming at similar purposes will be coded in separate modules in case
the logic behind the specific macro or processor be strongly coupled
with other component elements.
"""

__all__ = 'iGoogleGadgetMacro',

from trac.core import Interface, Component, ExtensionPoint, \
        implements, TracError
from trac.config import Option
from trac.mimeview.api import Context
from trac.util import get_pkginfo
from trac.web.api import IRequestHandler, RequestDone
from pkg_resources import resource_string, resource_filename
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor
from trac.web.api import IRequestHandler
from trac.web.chrome import ITemplateProvider, add_stylesheet
from trac.wiki.api import IWikiSyntaxProvider, parse_args
from trac.wiki.macros import WikiMacroBase
from trac.wiki.formatter import Formatter

from genshi.core import Markup
from genshi.builder import tag, Element

from os.path import join, exists
from os import makedirs
from itertools import chain
from urlparse import urlunparse
from urllib import urlencode

from tracgviz.api import ITracLinksHandler

__metaclass__ = type

class TracLinksFormatter(Formatter):
    """A wiki formatter which pays attention to nothing but trac 
    links.
    """
    for fmt_name in (x for x in Formatter.__dict__ \
            if x.endswith('_formatter') and \
            x not in ['_lhref_formatter', '_shref_formatter']):
        locals()[fmt_name] = lambda *args, **kwds: ''
    del fmt_name

class FirstTracLinkFormatter(TracLinksFormatter):
    """Gather the first TracLink found.
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
    """A quick and easy way to paste iGoogle gadgets in your wiki 
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
        """Resolve a TracLinks expression.
        
        @param link_text the TracLinks expression.
        @return the location (i.e. URL) this link is pointing to.
        """
        req, env, ctx = formatter.req, formatter.env, formatter.context
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
    
    def expand_macro(self, formatter, name, contents):
        _, args = parse_args(contents)
        self.log.debug('IG: iGoogleGadgetMacro -> args = %s', args)
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
