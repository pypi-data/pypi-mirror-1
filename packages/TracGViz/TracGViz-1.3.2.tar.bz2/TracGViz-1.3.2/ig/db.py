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

"""This module contains some Trac components so as to enhance Trac 
users experience, and to ease some common tasks related to gadgets 
and embedding them in wiki pages.

Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
Licensed under the Apache License, Version 2.0 
"""

from trac.core import Interface, Component, ExtensionPoint, implements
from trac.config import Option
from trac.util import get_pkginfo
from trac.web.api import IRequestHandler, RequestDone
from pkg_resources import resource_string, resource_filename
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor
from trac.web.api import IRequestHandler
from trac.web.chrome import ITemplateProvider, add_stylesheet

from os.path import join, exists, isabs
from os import makedirs, listdir
import types
from shutil import copyfileobj

from api import IGadgetBorderImgStore, BORDER_IMAGES

class DefaultBordersRepository(Component):
    """A repository that stores gadget border images under the 
    environment's `htdocs/gadgets/borders` folder.
    
    Images are stored in a directory inside the environment's 
    `htdocs/gadget/border` folder. This dir name matchs the name 
    chosen for the border id. Therefore the URL specified in the 
    gadget are available at URLs like :
    
    - http://<server>/<env>/chrome/site/gadget/border/<border_id>/
    
    ... or using any of the following TracLinks syntax:
    
    - htdocs:gadget/border/<border_id>/ (... in case )
    
    - gadget:border:<border_id>
    
    Note: The final slash MUST always be there, except in 
            TracLinks starting with `gadget:border` prefix.
    """
    implements(IEnvironmentSetupParticipant, IGadgetBorderImgStore)
    cfg_path = Option('gadgets', 'border_img_path', \
                        default=None, \
                        doc="The path where border images are stored."
                            " Defaults to the environment's "
                            "`htdocs/gadget/border` folder.")
    
    def __init__(self):
        self.log.info("IG: Configured path for gadget borders %s",\
                        repr(self.cfg_path))
        if not self.cfg_path:
            self.path = join(self.env.get_htdocs_dir(), 'gadget', 'border')
        elif not isabs(self.cfg_path):
            self.path = join(self.env.path, self.cfg_path)
        else:
            self.path = self.cfg_path
        self.log.info("IG: Image repository for gadget borders in %s",\
                        self.path)
    
    # IEnvironmentSetupParticipant methods
    def environment_created(self):
        """Create `htdocs/gadget/border` folder.
        """
        self.log.info('IG: Creating gadget borders folder in %s', self.path)
        makedirs(self.path)
    
    def environment_needs_upgrade(self, db):
        """Create `htdocs/gadget/border` folder if not already there.
        """
        if not exists(self.path):
            self.log.info('IG: Creating gadget borders folder in %s', \
                            self.path)
            makedirs(self.path)
        return False
    
    def upgrade_environment(self, db): pass
    
    # IGadgetBordersStore methods
    def _image_file_name(self, id, img_id):
        return join(self.path, id, img_id + '.gif')
    
    def store_images(self, id, **img_data):
        """Store gadget border images under the environment's 
        `htdocs/gadgets/borders` folder.
        """
        path = join(self.path, id)
        if not exists(path):
            makedirs(path)
        self.log.debug('IG: About to write image files for %s', id)
        # self.log.debug('IG: Image data %s', img_data)
        for img_id, contents in img_data.iteritems():
            if img_id in BORDER_IMAGES and contents:
                filename = self._image_file_name(id, img_id)
                self.log.debug('IG: Writing image file %s', filename)
                fo = file(filename, 'wb')
                if isinstance(contents, types.StringTypes):
                    fo.write(contents)
                else:
                    copyfileobj(contents, fo)
                fo.close()
        
    def load_image(self, id, img_id):
        """Retrieve the contents of a given picture in an image-based 
        gadget border.
        """
        fnm = self._image_file_name(id, img_id)
        if exists(fnm):
            try:
                return open(fnm, 'rb')
            except:
                self.log.exception('IG: Error reading image file %s', fnm)
                return None
        else:
            return None
    
    def enum_img_borders(self):
        """Return the name of the folders containing images.
        """
        return listdir(self.path)
