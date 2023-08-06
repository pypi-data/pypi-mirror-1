import os
import shutil

from canalweb import vod

ROOT = os.path.dirname(__file__)


class TestVOD(object):

    def setup_method(self, m):
        self.cache = os.path.join(ROOT, 'test-cache')
        try:
            shutil.rmtree(self.cache)
        except OSError:
            pass
        os.mkdir(self.cache)

        self.dl = vod.Downloader(self.cache)

    def test_content_ids(self):
        fd = open(os.path.join(ROOT, 'testdata', 'pid1830-c-zapping.html'))

        assert [url for url in self.dl.extract_content_ids(fd)] == [
            195190, 195164, 194541, 194196, 193817, 193423, 193128, 192859]

    def test_config(self):
        data = open(os.path.join(ROOT, 'testdata', 'video-config.xml')).read()
        video = self.dl._video_url(data, 'guignoles', 1234)

        assert video.url == (
            'http://vod-flash.canalplus.fr/WWWPLUS/PROGRESSIF'
            '/0812/LES_GUIGNOLS_EMISSION_081214_AUTO_1138_169_video_H.flv')
