"""VOD-related operations."""

import cookielib
import datetime
import logging
import os
import re
import urllib2
from xml.etree import ElementTree


class VOD(object):  # pylint: disable-msg=R0903
    """Represents a single video."""

    def __init__(self, url, show, vid, stamp):
        self.url = url
        self.show = show
        self.vid = vid
        self.date = stamp
        self.local_path = None

    def __cmp__(self, other):
        return cmp(self.url, other.url)

    def __hash__(self):
        return hash(self.url)

    def __repr__(self):
        return 'VOD(%r)' % (self.url,)

    def nice_date(self):
        if self.date:
            return self.date.strftime('%Y-%m-%d')
        return 'nodate'


class Downloader(object):
    """Download videos, possibly using locally cached data."""

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
        """Return the list of known videos for a show.

        Args:
          show: str, name of the show
        Returns:
          [VOD()] the known videos
        """
        videos = []
        for vid in self.extract_content_ids(self.fetch_html(show)):
            videos.append(self.fetch_config(show, vid))
        return videos

    def fetch_html(self, show):
        """Fetch the HTML page of a show."""
        url = self._URL_DOMAIN + self._SHOW_URL[show.nickname]

        txdata = None
        txheaders = {   
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US;'
            ' rv:1.8.1.7) Gecko/20070914 Firefox/2.0.0.7'
        }
        cookies = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
        request = urllib2.Request(url, txdata, txheaders)

        logging.info('fetching %s' % (url,))
        return opener.open(request)

    def extract_content_ids(self, stream):
        """Extract the show ids from the web page."""
        for line in stream:
            match = self._CONTENT_RE.search(line)
            if not match:
                continue
            yield int(match.group(1))

    def fetch_config(self, show, vid):
        """Get the URL of a video stream, possibly locally cached metadata."""
        target = os.path.join(self.cachedir, '%d-%d.xml' % (show.pid, vid))
        if os.path.exists(target):
            data = open(target).read()
        else:
            url = self._CFG_URL % {'video_id': vid, 'pid': show.pid}
            data = urllib2.urlopen(url).read().lstrip()
            open(target, 'w').write(data)

        return self._video_url(data, show, vid)

    @classmethod
    def _video_url(cls, data, show, vid):
        """Parse the XML metadata and extract the video strsm URL."""
        tree = ElementTree.ElementTree(ElementTree.XML(data))
        url = tree.find('//video/hi').text
        # heuristic to get date from filename...
        match = re.search(r'_(\d{6})_', url.split('/')[-1])
        if match:
            info = match.group(1)
            stamp = datetime.datetime(
                year=2000 + int(info[:2]),
                month=int(info[2:4]),
                day=int(info[4:6]))
        else:
            stamp = None
        return VOD(url, show, vid, stamp)

    def fetch_video(self, video):
        """Download a video if it is not locally available."""
        name = os.path.join(self.cachedir, '%s-%s-%s.flv' % (
            video.show.nickname, video.vid, video.nice_date()))
        video.local_path = name

        if os.path.exists(name):
            logging.info('%s already available' % (name,))
            return video

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
        return video
