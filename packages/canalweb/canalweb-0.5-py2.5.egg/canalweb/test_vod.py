"""Tests for canalweb.vod."""

# pylint: disable-msg=C0103,W0704,W0212,W0201

import os
import shutil

import canalweb
from canalweb import vod

ROOT = os.path.dirname(__file__)


class TestDownloader(object):
    """Test the Downloader class."""

    def setup_method(self, _):
        """Setup a downloader."""
        self.cache = os.path.join(ROOT, 'test-cache')
        try:
            shutil.rmtree(self.cache)
        except OSError:
            pass
        os.mkdir(self.cache)

        self.dl = vod.Downloader(self.cache)

    def test_content_ids(self):
        """Check exraction of video IDs."""
        fd = open(os.path.join(ROOT, 'testdata', 'pid1830-c-zapping.html'))

        assert [url for url in self.dl._extract_content_ids(fd)] == [
            195190, 195164, 194541, 194196, 193817, 193423, 193128, 192859]

    def test_config(self):
        """Check parsing of the XML file."""
        data = open(os.path.join(ROOT, 'testdata', 'video-config.xml')).read()
        show = canalweb.SHOW_BY_NICK['guignoles']
        video = self.dl._video_url(data, show, 1234)

        assert video.url == (
            'http://vod-flash.canalplus.fr/WWWPLUS/PROGRESSIF'
            '/0812/LES_GUIGNOLS_EMISSION_081214_AUTO_1138_169_video_H.flv')
