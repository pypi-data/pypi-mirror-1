"""Commandline interface for managing the videos."""

import logging
import optparse
import os
import sys

import canalweb

from canalweb import vod
from canalweb import xspf


def main(args=None):
    """Main entry point for the script."""
    if args is None:
        args = sys.argv[1:]

    parser = optparse.OptionParser(
        usage=('%prog [options] init | sync <show...> | list <show...>\n\n' +
               'Available shows: %s''' % (' '.join(sorted(canalweb.SHOW_BY_NICK)),)))
    parser.add_option('-c', '--cache',
                      action='store', dest='cache', default='.',
                      help='Directory in which to download files')

    (options, args) = parser.parse_args(args)

    # 'init': create the CANALWEB file
    # 'sync': download all files
    # 'list': list the available files
    if not args:
        parser.error('missing command')
    command = args.pop(0)

    logging.basicConfig(level=logging.DEBUG)

    cache = os.path.abspath(options.cache)
    marker = os.path.join(cache, 'CANALWEBCACHE')

    if command == 'init':
        logging.info('initializing new cache')
        if os.path.exists(marker):
            logging.error('directory already initialized')
            return 1
        open(marker, 'w').close()
        return 0

    # sanity check: have a predefined file in the cache directory
    if not os.path.exists(marker):
        logging.error('invalid cache location %r: initialize it first' % (
            cache,))
        return 1

    if command not in ('list', 'sync'):
        parser.error('unknown command %r' % (command,))

    if not args:
        parser.error('missing show names')

    try:
        shows = [canalweb.SHOW_BY_NICK[nick] for nick in args]
    except KeyError, e:
        parser.error('unknown show %r' % (e.args,))
        
    downloader = vod.Downloader(cache)

    if command == 'list':
        for show in shows:
            videos = downloader.get_video_info(show)
            for video in videos:
                print video.date, video.url

    elif command == 'sync':
        all_videos = []
        for show in shows:
            videos = downloader.get_video_info(show)
            videos.reverse()
            all_videos.extend(videos)
        for video in all_videos:
            downloader.fetch_video(video)
        open('playlist.xspf', 'w').write(xspf.videos_to_xspf(all_videos))
