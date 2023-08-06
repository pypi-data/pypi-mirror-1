import datetime

import canalweb
from canalweb import vod
from canalweb import xspf


def test_format_xspf():
    now = datetime.date(2008, 12, 12)

    videos = [
        vod.VOD('http://foo/bar', canalweb.SHOW_BY_NICK['zapping'], 456, now),
        vod.VOD('http://foo/baz', canalweb.SHOW_BY_NICK['zapping'], 457, now)
    ]
    videos[1].local_path = '/to/the/file'

    data = xspf.videos_to_xspf(videos)
    print data
    assert data == '''\
<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
  <title>Canal Web</title>
  <trackList>
    <track>
      <location>http://foo/bar</location>
      <title>Le Zapping 2008-12-12 (456)</title>
    </track>
    <track>
      <location>file:///to/the/file</location>
      <title>Le Zapping 2008-12-12 (457)</title>
    </track>
  </trackList>
</playlist>
'''
    
