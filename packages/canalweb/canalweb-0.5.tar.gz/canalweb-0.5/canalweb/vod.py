"""VOD-related operations."""

import cookielib
import datetime
import logging
import os
import re
import urllib2
from xml.etree import ElementTree

import canalweb


class VOD(object):  # pylint: disable-msg=R0903
    """Represents a single video."""

    def __init__(self, url, show, vid, stamp):
        self.url = url
        self.show = show
        self.vid = vid
        self.date = stamp
        self.local_path = None
        self.metadata = None

    def __cmp__(self, other):
        return cmp(self.url, other.url)

    def __hash__(self):
        return hash(self.url)

    def __repr__(self):
        return 'VOD(%s, %d)' % (self.show.nickname, self.vid)

    def nice_date(self):
        """Return a nicely formatted date for the show."""
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
        for vid in self._extract_content_ids(self._fetch_html(show)):
            vod = self.fetch_config(show, vid)
            if vod:
                videos.append(vod)
        return videos

    def get_cached_configs(self):
        """Return the list of shows locally cached."""
        md_dir = self._get_md_dir()
        videos = {}
        for filename in os.listdir(md_dir):
            parts = os.path.splitext(filename)[0].split('-')
            assert len(parts) == 2
            show, vid = (int(x) for x in parts)
            show = canalweb.SHOW_BY_PID[show]

            full_name = os.path.join(md_dir, filename)
            vod = self._video_url(open(full_name).read(), show, vid)
            if vod:
                vod.metadata = full_name
                videos.setdefault(show, set()).add(vod)
        return videos

    def _fetch_html(self, show):
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

    def _extract_content_ids(self, stream):
        """Extract the show ids from the web page."""
        for line in stream:
            match = self._CONTENT_RE.search(line)
            if not match:
                continue
            yield int(match.group(1))

    def _get_md_dir(self):
        """Return the location of the metadata cache."""
        md_dir = os.path.join(self.cachedir, '.metadata')
        if not os.path.isdir(md_dir):
            os.mkdir(md_dir)
        return md_dir

    def fetch_config(self, show, vid):
        """Get the URL of a video stream, possibly locally cached metadata."""
        md_dir = self._get_md_dir()
        target = os.path.join(md_dir, '%d-%d.xml' % (show.pid, vid))
        if os.path.exists(target):
            data = open(target).read()
        else:
            url = self._CFG_URL % {'video_id': vid, 'pid': show.pid}
            data = urllib2.urlopen(url).read().lstrip()
            open(target, 'w').write(data)

        vod = self._video_url(data, show, vid)
        if vod:
            vod.metadata = target
        return vod

    def _video_url(self, data, show, vid):
        """Parse the XML metadata and extract the video stream URL."""
        tree = ElementTree.ElementTree(ElementTree.XML(data))
        url = None
        for node in (tree.find('//video/hi'),
                     tree.find('//video/low')):
            if node is not None and node.text:
                url = node.text
                break
        else:
            return None
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
        vod = VOD(url, show, vid, stamp)
        vod.local_path = os.path.join(self.cachedir, '%s-%s-%s.flv' % (
            vod.show.nickname, vod.vid, vod.nice_date()))
        return vod

    @classmethod
    def fetch_video(cls, video):
        """Download a video if it is not locally available."""
        name = video.local_path
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

    @classmethod
    def delete_video(cls, video):
        """Delete metadata and video file."""
        if os.path.exists(video.local_path):
            os.unlink(video.local_path)
        if os.path.exists(video.metadata):
            os.unlink(video.metadata)
