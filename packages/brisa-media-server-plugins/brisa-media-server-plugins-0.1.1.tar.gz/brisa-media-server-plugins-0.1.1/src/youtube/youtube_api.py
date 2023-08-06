#!/usr/bin/env python

""" Simple YouTube.com API using python-gdata
"""

import re
import gdata.service
import urllib2

from brisa.core import log


class YoutubeClient(object):
    standart_feeds = 'http://gdata.youtube.com/feeds/api/standardfeeds'
    user_feeds = 'http://gdata.youtube.com/feeds/api/users'
    video_name_re = re.compile(r', "t": "([^"]+)"')

    def _request(self, r):
        service = gdata.service.GDataService(server='gdata.youtube.com')
        return service.Get(r)

    def featured(self):
        return self._request('%s/recently_featured' %
            self.standart_feeds).entry

    def favorite(self, username):
        return self._request('%s/%s/favorites' % (self.user_feeds,
                             username)).entry

    def uploaded(self, username):
        return self._request('%s/%s/uploads' % (self.user_feeds,
                             username)).entry

    def top_rated(self):
        return self._request('%s/top_rated' % self.standart_feeds).entry

    def most_viewed(self):
        return self._request('%s/most_viewed' % self.standart_feeds).entry

    def get_flv_url(self, url):
        flv = ''
        data = ''

        try:
            data = urllib2.urlopen(url).read()
        except:
            log.debug('Could not open URL %s' % url)

        if not data:
            return flv

        match = self.video_name_re.search(data)
        if match is not None:
            video_name = match.group(1)
            video_id = url.split('watch?v=')[1]

            flv = 'http://www.youtube.com/get_video?video_id=%s&t=%s'
            flv = flv % (video_id, video_name)

        return flv
