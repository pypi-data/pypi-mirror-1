# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>
# Some code from James Clarke <james@jamesclarke.info>

import webbrowser
import md5

from os import path
from urllib import urlencode, urlopen
from xml.etree import ElementTree
from commands import getoutput

from brisa.core import log


API_KEY = ''
SECRET = ''
HOST = 'http://flickr.com'
API = '/services/rest'
AUTH_API = '/services/auth'
CACHE_DIR = path.join(path.expanduser('~'), '.brisa')
username='brisa_project'


class FlickrError(Exception):
    pass


def _authenticate():
    token=_get_cached_token(username)
    if token == '':
        token = _renew_token()
    return token


def _get_cached_token(_username):
    token = ''
    uname = '"%s"' % _username
    try:
        f = open(path.join(CACHE_DIR, 'cached_tokens'), 'r')
        for line in f:
            if uname in line:
                token = line.split(':')[1]
                break
        f.close()
    except:
        token = ''
    return token


def _get_cached_nsid(_username):
    nsid = ''
    try:
        f = open(path.join(CACHE_DIR, 'cached_nsid'), 'r')
        for line in f:
            if line.__contains__('"'+_username+'"'):
                nsid=line.split(':')[1]
    except:
        nsid = ''
    return nsid


def _renew_token():
    # The app makes a background call to flickr.auth.getFrob:
    frob = get_frob()
    # The app lauch the browser
    auth_url=_getAuthURL('read', frob)
    call_browser_method(auth_url)
    token = get_token(frob)
    _cache_token(username, token)
    return token


def _getAuthURL(perms, frob):
    """
    Return the authorization URL to get a token.

    This is the URL the app will launch a browser toward if it
    needs a new token.

    perms -- "read", "write", or "delete"
    frob -- picked up from an earlier call to FlickrAPI.auth_getFrob()
    """
    data = {"api_key": API_KEY, "frob": frob, "perms": perms}
    data["api_sig"] = _generate_signature(data)
    url = str("%s%s?%s" % (HOST, AUTH_API, urlencode(data)))
    return url


def _generate_signature(data):
    """Calculate flickr signature.

    Calculate the flickr signature for a set of params.
    data -- a hash of all the params and values to be hashed, e.g.
    {"api_key":"AAAA", "auth_token":"TTTT"}
    """
    dataName = SECRET
    keys = data.keys()
    keys.sort()
    for a in keys:
        dataName += (a + data[a])
    hash = md5.new()
    hash.update(dataName)
    return hash.hexdigest()


def _cache_token(_email, token):
    f = open(path.join(CACHE_DIR, 'cached_tokens'), 'a')
    f.writelines('"%s":%s:\n'% (username, token))


def _cache_nsid(_email, nsid):
    f = open(path.join(CACHE_DIR, 'cached_nsid'), 'a')
    f.writelines('"%s":%s:\n'% (username, nsid))


def _get(method, auth=False, **params):
    """Get response from flickr API.

    Get the response from the flickr API for the given method with
    the given parameters.
    returns: The Element response for the method.
    """
    log.debug('Calling method: %s, with parameters %s', method, params)
    #convert lists to strings with ', ' between items
    for (key, value) in params.items():
        if isinstance(value, list):
            params[key] = ', '.join([item for item in value])
    if auth:
        params['auth_token'] = _authenticate()
        sig_params = params.copy()
        sig_params["api_key"] = API_KEY
        sig_params['method'] = method
        sig = _generate_signature(sig_params)
        params['api_sig'] = sig
    url = '%s%s/?method=%s&api_key=%s&%s'% \
          (HOST, API, method, API_KEY, urlencode(params))
    log.debug('Openning url: %s', url)

    try:
        response = urlopen(url)
    except IOError, e:
        log.debug('Error on flickr plugin: %s', e)
        return []
    response_element = ElementTree.parse(response).getroot()
    response.close()
    log.debug('Got response: \n%s', ElementTree.tostring(response_element))

    if not response_element.get('stat') == 'ok':
        error_et=response_element.find('err')
        msg = "ERROR [%s]: %s" % \
              (error_et.get('code'),
               error_et.get('msg'))
        raise FlickrError(msg)
    return response_element


## Flickr methods
# auth


def auth_getFrob():
    method = 'flickr.auth.getFrob'
    sig = _generate_signature({"api_key": API_KEY,
                               'method': method})
    return _get(method, api_sig=sig)


def auth_getToken(frob):
    method='flickr.auth.getToken'
    sig = _generate_signature({"api_key": API_KEY,
                               'method': method,
                               'frob': frob})
    return _get(method, api_sig=sig, frob=frob)


# people


def people_findByUsername(username):
    method = 'flickr.people.findByUsername'
    return _get(method, username=username)


def people_getPublicPhotos(user_id):
    method = 'flickr.people.getPublicPhotos'
    return _get(method, user_id=user_id)


# photos


def photos_search(user_id='', auth=False, tags='', tag_mode='', text='',
                  min_upload_date='', max_upload_date='',
                  min_taken_date='', max_taken_date='',
                  license='', per_page='', page='', sort=''):
    """Returns a list of Photo objects.

    If auth=True then will auth the user.  Can see private etc
    """
    method = 'flickr.photos.search'

    data = _get(method, auth=auth, user_id=user_id, tags=tags, text=text,
                min_upload_date=min_upload_date,
                max_upload_date=max_upload_date,
                min_taken_date=min_taken_date,
                max_taken_date=max_taken_date,
                license=license, per_page=per_page,
                page=page, sort=sort)
    return data


# interestingness


def interestingness_get_list():
    method = 'flickr.interestingness.getList'
    return _get(method)


# Hi level methods returns the apropriated strings, lists, dictionaries


def get_interesting_photos():
    """Get interesting photos of dictionaries.

    Get a list of dictionaries containing interresting photos from flickr.


    @return: list of dictionaries where 'url' and 'name' are keys and
    values according to the photo
    """
    photos_et = interestingness_get_list()
    photos = []
    append = photos.append
    if photos_et:
        for photo_et in photos_et.find('photos'):
            photo={}
            photo['url'] = get_photo_url(photo_et)
            photo['title'] = photo_et.get('title')
            photo['id'] = photo_et.get('id')
            append(photo)
    return photos


def get_frob():
    frob_et = auth_getFrob()
    return frob_et.find('frob').text


def get_token(frob):
    frob_et = auth_getToken(frob)
    if frob_et.find('auth').find('user').get('username') != username:
        actual_user=username
        logged_user=frob_et.find('auth').find('user').get('username')
        msg = 'You are trying to autenticate %s, but %s is already logged'%\
              (actual_user, logged_user)
        raise FlickrError(msg)
    return frob_et.find('auth').find('token').text


def get_user_nsid(username):
    nsid = _get_cached_nsid(username)
    if nsid == '':
        nsid = people_findByUsername(username).find('user').get('nsid')
        _cache_nsid(username, nsid)
    return nsid


def get_user_photos(username, private=False, size=None):
    nsid = get_user_nsid(username)
    if private:
        photos_et = photos_search(auth=True, user_id=nsid)
    else:
        photos_et = people_getPublicPhotos(nsid)
    photos = []
    if photos_et:
        append = photos.append
        for photo_et in photos_et.find('photos'):
            photo={}
            photo['id'] = photo_et.get('id')
            photo['url'] = get_photo_url(photo_et, size)
            photo['title'] = photo_et.get('title')
            append(photo)
    return photos


def get_photos_urls(photos_et, size=None):
    """Size Suffixes.

    The letter suffixes are as follows:
    s    small square 75x75
    t    thumbnail, 100 on longest side
    m    small, 240 on longest side
    None medium, 500 on longest side
    b    large, 1024 on longest side
    """

    return [get_photo_url(photo_et, size)\
            for photo_et in photos_et.find('photos')]


def get_photo_url(photo_et, size=None):
    if size not in ['s', 't', 'm', 'b']:
        return ('http://farm%s.static.flickr.com/%s/%s_%s.jpg' %\
                (photo_et.get('farm'),
                 photo_et.get('server'),
                 photo_et.get('id'),
                 photo_et.get('secret')))
    else:
        return ('http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg' %\
                (photo_et.get('farm'),
                 photo_et.get('server'),
                 photo_et.get('id'),
                 photo_et.get('secret'),
                 size))


def call_browser(url):
    browser = webbrowser.get().name
    command = browser + '"' + url + '"'
    getoutput(command)
    getoutput('sleep 10')

call_browser_method=call_browser
