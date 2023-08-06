# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

from brisa_media_server.plugins.flickr import brisa_flickr
from brisa.upnp.didl.didl_lite import Photo, Container, Resource
from brisa.core.plugin import PluginInterface
from brisa.core import log, config


log = log.getLogger('plugin.flickr')
plugin_section = 'media_server_plugin-flickr'


class FlickrPlugin(PluginInterface):
    """ Plugin to access an flickr account.
    """
    name = 'flickr'
    private = config.get_parameter_bool(plugin_section, 'private')
    usage = config.get_parameter_bool(plugin_section, 'enable')
    username = config.get_parameter(plugin_section, 'username')
    brisa_flickr.API_KEY = 'f544dbc725689997313a6437e1068b5a'
    brisa_flickr.SECRET = '3281387735c48555'
    containers = {}

    def load(self):
        rp = self.plugin_manager.root_plugin

        images_container = rp.get_container('Images')
        remote_container = rp.get_container('Remote Images')

        if not images_container:
            images_container = rp.add_container('Images', 0)
        if not remote_container:
            remote_container = rp.add_container('Remote Images',
                                                images_container.id)

        self.container = rp.add_container('Flickr',
                                          remote_container.id,
                                          self)

        # Subcontainers
        self.user_container = rp.add_container('User Photos (%s)' % \
                                               self.username,
                                               self.container.id,
                                               self)
        self.interesting_container = rp.add_container('Interesting Photos',
                                                      self.container.id,
                                                      self)

        self.containers[str(self.user_container.id)] = self.user_container
        self.containers[str(self.interesting_container.id)] = \
            self.interesting_container

    def unload(self):
        pass

    def browse(self, id, browse_flag, filter, starting_index,
                requested_count, sort_criteria):
        # Browse root container
        if id == self.container.id:
            return self.containers.values()
        # Browse a subcontainer
        elif id in self.containers:
            if not self.containers[id].items:
                # Load items
                if id == self.user_container.id:
                    photos = self._get_user_photos()
                    container = self.user_container

                elif id == self.interesting_container.id:
                    photos = brisa_flickr.get_interesting_photos()
                    container = self.interesting_container

                untitled_count = 0

                for p in photos:
                    if not p['title']:
                        p['title'] = 'Untitled %d' % untitled_count
                        untitled_count += 1

                    item = Photo(p['id'], self.user_container.id, p['title'])
                    item.add_resource(Resource(p['url'],
                                               'http-get:*:image/jpeg:*'))
                    container.add_item(item)

            return self.containers[id].items
        # Browse item
        else:
            return self._get_item(id)

    def _get_user_photos(self):
        username = config.get_parameter(plugin_section, 'username')
        isprivate = config.get_parameter_bool(plugin_section, 'private')
        brisa_flickr.username = username
        return brisa_flickr.get_user_photos(username, isprivate)

    def _get_item(self, id):
        for c in self.containers.values():
            for item in c.items:
                if id == item.object_id.split(':')[1]:
                    return [item]
        return []
