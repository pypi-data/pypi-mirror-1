# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

import ConfigParser

from urllib import urlopen, urlencode
from xml.etree import ElementTree
from os import path

from brisa.core import log


class BrisaShoutcast(object):
    cache = ConfigParser.SafeConfigParser()
    cache_file = path.join(path.expanduser('~'), '.brisa', 'cached_stations')
    log = log.getLogger('shoutcast')

    def _get_cached_stream(self, id):
        f=open(self.cache_file)
        self.cache.read(f)
        return self.cache.get(id, 'url')

    def _add_to_cache(self, id, stream):
        try:
            f=open(self.cache_file, 'r+')
        except:
            f=open(self.cache_file, 'w')
            self.log.debug('Creating shoutcast station cache')
        self.cache.add_section(id)
        self.cache.set(id, 'url', stream)
        self.cache.write(f)

    def _id_is_cached(self, id):
        try:
            f=open(self.cache_file)
            self.cache.readfp(f)
            cached = self.cache.has_section(id)
            return cached
        except:
            return False

    def _alternative_station_list(self):
            query = {'genre': 'top',
                     'mt': 'audio/mpeg',
                     'br': '128'}
            params = urlencode(query)
            url = 'http://www.shoutcast.com/sbin/newxml.phtml?%s'%(params)
            self.log.debug('openning alternative url: %s', url)
            response = urlopen(url)
            return ElementTree.parse(response).getroot()

    def station_url(self, id):
        cached = self._id_is_cached(id)
        if cached:
            return self._get_cached_stream(id)
        query = {'id': id}
        params = urlencode(query)
        url = 'http://www.shoutcast.com/sbin/tunein-station.pls?%s'%(params)
        playlist_file = urlopen(url+params)
        config = ConfigParser.SafeConfigParser()
        config.readfp(playlist_file)
        stream = config.get('playlist', 'File1')
        if not cached:
            self._add_to_cache(id, stream)
        return stream

    def station_list(self):
        query = {'genre': 'Top500',
                 'mt': 'audio/mpeg',
                 'br': '128'}
        params = urlencode(query)
        url = 'http://www.shoutcast.com/sbin/newxml.phtml?%s'%(params)
        self.log.debug('openning url: %s', url)
        response = urlopen(url)
        try:
            radios_et = ElementTree.parse(response).getroot()
        except:
            radios_et = self._alternative_station_list()
        stations = []
        for station_et in radios_et:
            station={}
            station['bitrate']=station_et.get('br')
            station['name']=station_et.get('name')
            station['genre']=station_et.get('genre')
            station['id']=station_et.get('id')
            if station['id']:
                stations.append(station)
        return stations

    def station_list_by_genre(self, genre, port_list=None):
        query = {'genre': genre,
                 'mt': 'audio/mpeg',
                 'limit': '40'}
        params = urlencode(query)
        url = 'http://www.shoutcast.com/sbin/newxml.phtml?%s'%(params)
        self.log.debug('openning url: %s', url)
        response = urlopen(url)
        try:
            radios_et = ElementTree.parse(response).getroot()
        except:
            radios_et = self._alternative_station_list()
        stations = []
        for station_et in radios_et:
            station={}
            station['bitrate']=station_et.get('br')
            station['name']=station_et.get('name')
            station['genre']=station_et.get('genre')
            station['id']=station_et.get('id')
            if station['id']:
                try:
                    station['url']=self.station_url(station['id'])
                except Exception, e:
                    continue
                stations.append(station)
        if port_list is not None:
            stations=self._filter_stations_by_port(stations, port_list)
        return stations

    def _filter_stations_by_port(self, list, port_list):
        new_list = []
        append = new_list.append
        for station in list:
            port = station['url'].split(':')[2].split('/')[0]
            if port in port_list:
                append(station)
        return new_list

    def _genre_list(self):
            genre_list = []
            url = 'http://www.shoutcast.com/sbin/newxml.phtml?'
            response = urlopen(url)
            genre_et = ElementTree.parse(response).getroot()
            get = genre.get
            return [get('name') for genre in genre_et]
