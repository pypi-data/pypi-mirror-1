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

r"""Trac Data Sources for Google Visualization API. Embed iGoogle gadgets using WikiFormatting.

This package (plugin) provides components so that Trac be able to
use widgets and related technologies provided by Google.

- It allows to feed data managed by Trac to widgets based on Google 
  Visualization API. 
- It allows embedding iGoogle Gadgets in wiki pages using WikiFormatting.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

# Ignore errors to avoid Internal Server Errors
from trac.core import TracError
TracError.__str__ = lambda self: unicode(self).encode('ascii', 'ignore')

__all__ = 'TracGVizSystem', 'GViz_0_5', 'GVizJsonEncoder'\
            'GVizCSVEncoder', 'GVizHtmlEncoder'

try:
    from api import TracGVizSystem
    from rpc import *
    from stdhash import *
    from proto import GViz_0_5
    from stdfmt import GVizJsonEncoder, GVizHtmlEncoder, GVizCSVEncoder
    from extfmt import *
    from ticket import *
    from wiki import *
    from search import *
    from timeline import *
    from vcs import *
    from ig import *
    msg = 'Ok'
except Exception, exc:
#    raise
    msg = "IG: Exception %s raised: '%s'" % (exc.__class__.__name__, str(exc))
