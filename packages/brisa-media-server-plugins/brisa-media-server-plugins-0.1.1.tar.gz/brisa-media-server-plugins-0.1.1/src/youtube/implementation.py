# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2008 Brisa Team <brisa-develop@garage.maemo.org>

from brisa.core import log, config
from brisa.core.plugin import PluginInterface
from brisa.utils import properties
from brisa.upnp.didl.didl_lite import VideoBroadcast, Resource

from youtube_api import YoutubeClient


plugin_section = 'media_server_plugin-youtube'
youtube_video_url = config.get_parameter(plugin_section, 'video_url')


class YouTubePlugin(PluginInterface):
    name = 'youtube'
    usage = config.get_parameter_bool(plugin_section, 'enable')
    username = config.get_parameter(plugin_section, 'username')
    containers = {}
    containers_cb = {}

    def __init__(self):
        self.client = YoutubeClient()

    def load(self):
        rp = self.plugin_manager.root_plugin

        videos_container = rp.get_container('Videos')
        remote_videos_container = rp.get_container('Remote Videos')

        if not videos_container:
            videos_container = rp.add_container('Videos', 0)
        if not remote_videos_container:
            remote_videos_container = rp.add_container('Remote Videos',
                                                       videos_container.id)

        self.youtube_root_cont = rp.add_container('Youtube',
                                                  remote_videos_container.id,
                                                  self)

        self.upload_container = rp.add_container('%s Uploaded Videos' %
                                                self.username,
                                                self.youtube_root_cont.id,
                                                self)

        self.containers[self.upload_container.id] = self.upload_container
        self.containers_cb[self.upload_container.id] = \
            self._get_uploaded_videos

        self.favorite_container = rp.add_container('%s Favorite Videos' %
                                                 self.username,
                                                 self.youtube_root_cont.id,
                                                 self)

        self.containers[self.favorite_container.id] = self.favorite_container
        self.containers_cb[self.favorite_container.id] = \
            self._get_favorite_videos

        self.featured_container = rp.add_container('Featured Videos',
                                                   self.youtube_root_cont.id,
                                                   self)

        self.containers[self.featured_container.id] = self.featured_container
        self.containers_cb[self.featured_container.id] = \
            self._get_featured_videos

    def unload(self):
        pass

    def _get_uploaded_videos(self):
        """ Returns a list of VideoBroadcast items representing uploaded videos
        of the user.
        """
        uploaded = []

        for video in self.client.uploaded(self.username):
            url = self.client.get_flv_url('%s%s' % (youtube_video_url,
                                          video.id.text.split('/')[-1]))
            if not url:
                continue
            item = VideoBroadcast('youtube:%s' % video.id.text.split('/')[-1],
                                  self.upload_container.id,
                                  video.title.text,
                                  producers=[str(a.name) for a in \
                                     video.author],
                                  description=video.content.text)
            item.add_resource(Resource(url, 'http-get:*:video/flv:*'))
            uploaded.append(item)

        return uploaded

    def _get_favorite_videos(self):
        """ Returns a list of VideoBroadcast items representing favorite videos
        of the user.
        """
        favorites = []

        for video in self.client.favorite(self.username):
            url = self.client.get_flv_url('%s%s' % (youtube_video_url,
                                          video.id.text.split('/')[-1]))
            if not url:
                continue
            item = VideoBroadcast('youtube:%s' % video.id.text.split('/')[-1],
                                  self.favorite_container.id,
                                  video.title.text,
                                  producers=[str(a.name) for a in \
                                    video.author],
                                  description=video.content.text)
            item.add_resource(Resource(url, 'http-get:*:video/flv:*'))
            favorites.append(item)

        return favorites

    def _get_featured_videos(self):
        """ Returns a list of VideoBroadcast items representing featured videos
        on youtube main page.
        """
        featured = []

        for video in self.client.featured():
            url = self.client.get_flv_url('%s%s' % (youtube_video_url,
                                          video.id.text.split('/')[-1]))
            if not url:
                continue
            item = VideoBroadcast('youtube:%s' % video.id.text.split('/')[-1],
                                  self.featured_container.id,
                                  video.title.text,
                                  producers=[str(a.name) for a in \
                                    video.author],
                                  description=video.content.text)
            item.add_resource(Resource(url, 'http-get:*:video/flv:*'))
            featured.append(item)

        return featured

    def _get_video(self, id):
        for c in self.containers.values():
            for i in c.items:
                if i.id == id:
                    return [i]
        return []

    def browse(self, id, browse_flag, filter, starting_index,
               requested_count, sort_criteria):
        if id == self.youtube_root_cont.id:
            return self.containers.values()
        elif id in self.containers:
            if not self.containers[id].items:
                self.containers[id].items = self.containers_cb[id]()
            return self.containers[id].items
        else:
            return self._get_video(id)
