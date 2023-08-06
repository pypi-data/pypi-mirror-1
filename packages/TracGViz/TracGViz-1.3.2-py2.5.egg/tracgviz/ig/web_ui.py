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

from trac.core import Interface, Component, ExtensionPoint, \
        implements, TracError
from trac.config import Option
from trac.util import get_pkginfo
from trac.web.api import IRequestHandler, RequestDone
from pkg_resources import resource_string, resource_filename
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor
from trac.util.translation import _
from trac.web.api import IRequestHandler
from trac.web.chrome import ITemplateProvider, add_stylesheet, \
        add_warning

from genshi.builder import tag

from os.path import join, exists, basename
from os import makedirs

from api import IGadgetBorderImgStore, BORDER_IMAGES, \
        IGadgetBorderProvider
from tracgviz.api import ITracLinksHandler

try:
    from tracgviz.util import send_response, send_std_error_response
except ImportError:
    # Installation issue :(
    from util import send_response, send_std_error_response

class GadgetsBorderModule(Component):
    """Upload pictures so that Trac be able to host them 
    for later use in image-based gadget borders. Besides ensure 
    that the images are suitable for this particular purpose (e.g. 
    that dimensions are according to the specifications).
    
    Each border is identified by a string token specified by users at
    upload time, and consists of a group of images having the 
    following names and dimensions :
    
    - 1x28: b.gif, tt.gif
    - 1x12: tn.gif
    - 8x1: l.gif, r.gif
    - 8x28: bl.gif, br.gif, tl.gif, tr.gif
    
    Fore more details about image-based gadget borders, please visit 
    http://code.google.com/apis/gadgets/docs/legacy/publish.html#Borders
    
    Image storage is handled by the active gadget data repository.
    """
    implements(# IPermissionRequestor, \
            IRequestHandler, ITemplateProvider, IGadgetBorderProvider, \
            ITracLinksHandler)
    stores = ExtensionPoint(IGadgetBorderImgStore)
    
    store_name = Option('gadgets', 'border_img_store', \
                        default='DefaultBordersRepository', \
                        doc='The name of the component used to store'
                            'gadget border images.')
    
    def __init__(self):
        self.store = None
        self.log.debug('IG: Setting up gadget border store')
        for store in self.stores:
            if store.__class__.__name__ == self.store_name:
                self.store = store
                self.log.debug('IG: Gadget border store %s', self.store)
                break
        if not self.store:
            raise TracError('Missing border store')
    
    # IPermissionRequestor methods
    
    # IRequestHandler methods
    def match_request(self, req):
        """Return whether the requested path starts with 
        `/gadget/ig/border` prefix or not.
        """
        url_path = req.path_info
        self.log.debug("IG: URL path '%s'", url_path)
        if url_path.startswith('/gadget/ig/border'):
            try:
                return url_path[17] == '/'
            except IndexError:
                return True
        return False
    
    def process_request(self, req):
        """If no parameters are specified then show a web interface
        to create a new (update an existing) image-based gadget 
        border. Otherwise assume this request has been sent so as to
        update the associated images files.
        """
        ctx = dict(fields=None)
        target = req.path_info[18:]
        if target:
            try:
                id, filename = target.split('/')
                filename = filename[:-4]    # Prune .gif suffix
                if filename not in BORDER_IMAGES:
                    raise ValueError()
                else:
                    fo = self.store.load_image(id, filename )
                    if fo is None:
                        self.log.exception('Image in %s not found', target)
                        raise ValueError()
                    send_response(req, 200, fo.read(), \
                                    mimetype='image/gif')
                    fo.close()
            except RequestDone:
                raise
            except ValueError:
                # TODO: Send standard picture
                send_std_error_response(req, 404)
            except:
                self.log.exception('IG: Failed to load image in %s', target)
                send_std_error_response(req, 500)
        elif req.args.get('action') == 'new':
            try:
                id = req.args['id']
            except KeyError:
                add_warning(req, 'Border id cannot be empty')
                ctx = dict(fields=req.args)
            else:
                if id:
                    self.log.debug("IG: Handling image submission")
                    img_data = dict()
                    # self.log.debug("IG: Args in request %s", req.args)
                    try:
                        for img_id in BORDER_IMAGES:
                            upload = req.args.get(img_id, None)
                            if upload is None or isinstance(upload, unicode) \
                                    or not upload.filename:
                                continue
                            self.log.debug("IG: Uploaded file %s", type(upload))
                            filename = upload.filename.replace('\\', '/').replace(':', '/')
                            filename = basename(filename)
                            if filename:
                                img_data[img_id] = upload.file
                        self.store.store_images(id, **img_data)
                    except Exception, exc:
                        self.log.exception('IG: Image submission failed')
                        add_warning(req, "Image submission failed with " \
                                    "message : %s " % (str(exc),))
                        ctx = dict(fields=req.args)
                else:
                    add_warning(req, 'Border id cannot be empty')
                    ctx = dict(fields=req.args)
        add_stylesheet(req, 'common/css/admin.css')
        add_stylesheet(req, 'common/css/wiki.css')
        return ('ig_border_edit.html', ctx, None)
        # TODO: Implement image upload.
    
    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        """Return the path to the `htdocs` folder.
        """
        yield ('ig', resource_filename('tracgviz.ig', 'htdocs'))
    
    def get_templates_dirs(self):
        """Return the path to the `templates` folder.
        """
        yield resource_filename('tracgviz.ig', 'templates')
    
    def get_namespace(self):
        """ Install in `local.img` namespace.
        """
        return ('local', 'img')
    
    def get_border_spec(self, border_id):
        """Retrieve an image-based border specification.
        
        @param border_id a string identifying the target border
        @return the URL pointing to the border image set
        """
        env_url = self.env.base_url
        if not env_url:
            raise TracError("Environment has no reference URL "
                            "please set trac:base_url in trac.ini")
        if env_url[-1] != '/':
            env_url+= '/'
        return env_url + 'gadget/ig/border/' + border_id + '/'
    
    def get_description(self):
        return "Border images hosted by Trac."
    
    def enum_borders(self):
        """List all the borders stored in the images repository.
        
        @return a sequence containing all the available border ids
        """
        return self.store.enum_img_borders()

    # ITracLinksHandler methods
    def _format_link(self, formatter, ns, border_id, label):
        title = border_id + " (Gadget border)"
        if not label:
            label = title
        url = self.get_border_spec(border_id)
        return tag.a(label, class_='wiki', href= url, title=title)
    
    def get_link_resolvers(self):
        """Return an iterable over (namespace, formatter) tuples.

        Each formatter should be a function of the form
        fmt(formatter, ns, target, label), and should
        return some HTML fragment.
        The `label` is already HTML escaped, whereas the `target` is not.
        """
        yield (('gadget', 'border', 'image'), self._format_link)
