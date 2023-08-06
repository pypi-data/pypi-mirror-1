# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

from brisa.core import config
from brisa.core.plugin import PluginInterface
from brisa.upnp.didl.didl_lite import AudioBroadcast, Container, Resource

from brisa_shoutcast import BrisaShoutcast

plugin_section = 'media_server_plugin-shoutcast'


class ShoutCastPlugin(PluginInterface):
    """ SHOUTcast plugin.

    Obtains the urls of the shoutcast stations from www.shoutcast.com
    """
    name = 'shoutcast'
    genre_list = ['Adult', 'Alternative', 'Ambient', 'Blues', 'Christian',
                  'Classical', 'Country', 'Dance', 'Euro', 'Electronic',
                  'Folk', 'Jazz', 'Latin', 'Metal', 'News', 'Oldies',
                  'Progressive', 'Punk', 'Rap', 'Reggae', 'Rock', 'Soundtrack',
                  'Sport', 'Soul', 'World']
    usage = config.get_parameter_bool(plugin_section, 'enable')
    containers = {}

    def __init__(self):
        self.allowed_ports = config.get_parameter_as_list(plugin_section,
                                                          'ports', ':')
        if self.allowed_ports[0] == '0':
            self.allowed_ports = None

        self.shoutcast = BrisaShoutcast()

    def register(self):
        rp = self.plugin_manager.root_plugin

        audio_container = rp.get_container('Audio')
        remote_audio_container = rp.get_container('Remote Audios')

        if not audio_container:
            audio_container = rp.add_container('Audio', 0)

        if not remote_audio_container:
            remote_audio_container = rp.add_container('Remote Audios',
                                                      audio_container.id)

        self.container = rp.add_container('SHOUTcast Stations',
                                          remote_audio_container.id,
                                          self)

    def load(self):
        self.register()

    def unload(self):
        pass

    def register_genre_items(self, id):
        for station in \
            self.shoutcast.station_list_by_genre(self.containers[id].title,
            self.allowed_ports):
            item = AudioBroadcast('shoutcast:station-%s' % station['id'],
                                  self.container.id, station['name'],
                                  radio_station_id=station['id'])
            item.add_resource(Resource(station['url'], '*:*:audio/broadcast:*',
                              bitrate=station['bitrate']))
            self.containers[id].add_item(item)

    def get_item(self, id):
        for c in self.containers.values():
            for i in c.items:
                if id == i.id:
                    return [i]
        return []

    def browse(self, id, browse_flag, filter, starting_index,
                requested_count, sort_criteria):
        if id == self.container.id:
            if not self.containers:
                for g in self.genre_list:
                    self.containers['shoutcast:%s' % g] = \
                        Container('shoutcast:%s' % g, self.container.id, g)
            return self.containers.values()
        elif id in self.containers:
            if not self.containers[id].items:
                self.register_genre_items(id)
            return self.containers[id].items
        else:
            return self.get_item(id)
