"""VOD-related operations."""

import cookielib
import datetime
import logging
import os
import re
import urllib2
from xml.etree import ElementTree

from canalweb import flvread


class VOD(object):
    """Represents a single video."""

    def __init__(self, url, show, vid, stamp):
        self.url = url
        self.show = show
        self.vid = vid
        self.date = stamp

    def __cmp__(self, other):
        return cmp(self.url, other.url)

    def __hash__(self):
        return hash(self.url)

    def __repr__(self):
        return 'VOD(%r)' % (self.url,)


class Downloader(object):

    _SHOW_ID = {
        'zapping': 1830,
        'guignoles': 1784,
        'magzin': 1787
    }

    _URL_DOMAIN = 'http://www.canalplus.fr'

    _SHOW_URL = {
        'zapping': '/c-infos-documentaires/pid1830-c-zapping.html',
        'guignoles': '/c-humour/pid1784-c-les-guignols.html',
        'magzin': '/c-humour/pid1787-c-groland.html',
    }

    _CONTENT_RE = re.compile(r'CONTENT_ID.*=\s*["\'](\d+)')

    _CFG_URL = ('http://www.canalplus.fr/flash/xml/module/embed-video-player'
                '/embed-video-player.php?video_id=%(video_id)s&pid=%(pid)d')

    def __init__(self, cachedir):
        self.cachedir = cachedir

    def get_video_info(self, show):
        videos = []
        for vid in self.extract_content_ids(self.fetch_html(show)):
            videos.append(self.fetch_config(show, vid))
        return videos

    def fetch_html(self, show):
        url = self._URL_DOMAIN + self._SHOW_URL[show]

        txdata = None
        txheaders = {   
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.7)'
            ' Gecko/20070914 Firefox/2.0.0.7'
        }
        cookies = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
        request = urllib2.Request(url, txdata, txheaders)

        logging.info('fetching %s' % (url,))
        return opener.open(request)

    def extract_content_ids(self, stream):
        for line in stream:
            m = self._CONTENT_RE.search(line)
            if not m:
                continue
            yield int(m.group(1))

    def fetch_config(self, show, vid):
        pid = self._SHOW_ID[show]
        target = os.path.join(self.cachedir, '%d-%d.xml' % (pid, vid))
        if os.path.exists(target):
            data = open(target).read()
        else:
            url = self._CFG_URL % {'video_id': vid, 'pid': pid}
            data = urllib2.urlopen(url).read().lstrip()
            open(target, 'w').write(data)

        return self._video_url(data, show, vid)

    def _video_url(self, data, show, vid):
        tree = ElementTree.ElementTree(ElementTree.XML(data))
        url = tree.find('//video/hi').text
        # heuristic to get date from filename...
        m = re.search(r'_(\d{6})_', url.split('/')[-1])
        if m:
            info = m.group(1)
            stamp = datetime.datetime(
                year=2000 + int(info[:2]),
                month=int(info[2:4]),
                day=int(info[4:6]))
        else:
            stamp = None
        return VOD(url, show, vid, stamp)

    def fetch_video(self, video):
        name = os.path.join(
            self.cachedir, '%s-%s-%s.flv' % (
            video.show, video.vid, video.date or 'nodate'))
        if os.path.exists(name):
            logging.info('%s already available' % (name,))
            return name

        logging.info('downloading %s' % (video.url,))

        filename = name + '.tmp'
        dst = open(filename, 'w')
        src = urllib2.urlopen(video.url)
        while True:
            block = src.read(256 * (2 ** 10))
            dst.write(block)
            if not block:
                break
        dst.close()
        
        os.rename(filename, name)
        return name
