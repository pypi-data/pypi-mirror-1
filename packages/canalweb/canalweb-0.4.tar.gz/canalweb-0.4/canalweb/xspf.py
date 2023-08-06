"""Generate a playlist in XSPF format."""

from xml.sax import saxutils

def videos_to_xspf(videos):
    tracks = []
    for video in videos:
        if video.local_path:
            url = 'file://' + video.local_path
        else:
            url = video.url
        url = saxutils.escape(url)

        title = u'%s %s (%d)' % (
            video.show.fullname, video.nice_date(), video.vid)
        title = saxutils.escape(title.encode('utf-8'))

        tracks.append('''\
    <track>
      <location>%(location)s</location>
      <title>%(title)s</title>
    </track>''' % {'title': title, 'location': url})
        
    return '''\
<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
  <title>Canal Web</title>
  <trackList>
%s
  </trackList>
</playlist>
''' % ('\n'.join(tracks),)
