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

"""Core components to integrate Trac with Google Gadgets technology
(i.e. iGoogle container). 

This package states how to enhance and extend the different features
available in Trac Gadgets subsystem. The goal for all this 
extensibility is to ease the process of embedding gadgets in Trac 
site by providing easy-to-use wiki formatting constructs.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

from trac.core import Interface, Component, ExtensionPoint, implements
from trac.config import Option
from trac.util import get_pkginfo
from trac.web.api import IRequestHandler, RequestDone
from trac.wiki.api import IWikiSyntaxProvider
from pkg_resources import resource_string, resource_filename

from genshi.builder import tag

from os import listdir, environ
from os.path import isdir

class IGadgetBorderImgStore(Interface):
    """The interface implemented by the components responsible for
    storing the pictures to use in gadgets borders, and keep track of
    the border sets.
    
    Images are stored in a directory inside the environment's 
    `htdocs/gadget/border` folder. This dir name matchs the name 
    chosen for the border id. Therefore the URL specified in the 
    gadget are available at URLs like :
    
    - http://<server>/<env>/chrome/site/gadget/border/<border_id>/
    
    ... or using any of the following TracLinks syntax:
    
    - htdocs:gadget/border/<border_id>/
    
    - gadget:border:<border_id>
    
    The latest is the most portable way (and therefore is 
    recommended) since images might be stored in a different
    repository.
    
    Note: The final slash MUST always be there, except in 
            TracLinks starting with `gadget:border` prefix.
    """
    def store_images(id, tl, tr, bl, br, l, r, b, tt, tn):
        """Store the images in an image-based gadget border.
        
        @param id the border identifier
        @param tl the contents of the top-left corner image
        @param tr the contents of the top-right corner image
        @param bl the contents of the bottom-left corner image
        @param br the contents of the bottom-right corner image
        @param l the contents of the left side image
        @param r the contents of the right side image
        @param b  the contents of the bottom image
        @param tt the contents of the top level image (with title)
        @param tn  the contents of the top level image (no title)
        
        Note: All the previous values (except `id`) may also be file 
                objects from where contents will be retrieved.
        """
    def load_image(id, img_id):
        """Retrieve the contents of a picture in an image-based 
        gadget border.
        
        @param id the border identifier
        @param img_id one of `tl`, `tr`, `bl`, `br`, `l`, `r`, `b`, 
                    `tt`, `tn` so as to identify the requested image
        @return a file-like object used to retrieve the image contents
                    or `None` if such file does not exists
        """

BORDER_IMAGES = ['tl', 'tr', 'bl', 'br', 'l', 'r', 'b', 'tt', 'tn']

class IGadgetBorderProvider(Interface):
    """Interface implemented by all those components offering borders
    gadgets will be surronded with. This includes both image-based 
    and CSS-based borders.
    """
    def get_namespace():
        """Specify the namespace identifying this borders provider.
        
        @return a string or sequence of strings
        """
    def get_border_spec(border_id):
        """Retrieve the string to set the `border` parameter in the 
        URL needed to paste the gadget into the HTML of the target 
        web page.
        
        @param border_id a string identifying the target border
        @return a string value formatted as explained for gatget 
                borders in iGoogle Gadgets specification.
                See code.google.com/apis/gadgets/docs/legacy/publish.html#Borders
                for more details.
        """
    def get_description():
        """Describe this border provider.
        
        @return an informative string describing this border provider.
        """
    def enum_borders():
        """List all the borders managed by this particular 
        border provider.
        
        @return a sequence containing all the available border ids
        """

class GadgetBordersManager(Component):
    """Component responsible for managing gadget borders.
    """
    bprov = ExtensionPoint(IGadgetBorderProvider)
    
    # TODO : Implement
    def __init__(self):
        self.providers = dict([p.get_namespace(), p] for p in self.bprov)
    

