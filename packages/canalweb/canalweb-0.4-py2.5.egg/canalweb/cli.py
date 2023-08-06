"""Commandline interface for managing the videos."""

import logging
import optparse
import os
import sys
import ConfigParser

import canalweb

from canalweb import vod
from canalweb import xspf


def get_config(marker):
    """Parse the config from the specified file."""
    parser = ConfigParser.SafeConfigParser()
    parser.readfp(open(marker))

    if not parser.has_section('seen'):
        parser.add_section('seen')
    return parser


def set_config(marker, parser):
    """Store the updated config."""
    parser.write(open(marker, 'w'))


def main(args=None):
    """Main entry point for the script."""
    if args is None:
        args = sys.argv[1:]

    parser = optparse.OptionParser(
        usage=('%prog [options] init | sync <show...> | seen <show...>\n\n' +
               'Available shows: %s''' % (
        ' '.join(sorted(canalweb.SHOW_BY_NICK)),)))
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

    if command not in ('sync', 'seen'):
        parser.error('unknown command %r' % (command,))

    if not args:
        parser.error('missing show names')

    try:
        shows = [canalweb.SHOW_BY_NICK[nick] for nick in args]
    except KeyError, error:
        parser.error('unknown show %r' % (error.args,))
        
    downloader = vod.Downloader(cache)
    all_videos = downloader.get_cached_configs()
    parser = get_config(marker)

    if command == 'sync':
        for show in shows:
            # these are all the videos available right now
            videos = all_videos.get(show, set())
            videos.update(downloader.get_video_info(show))

            if parser.has_option('seen', show.nickname):
                last_seen = parser.getint('seen', show.nickname)
            else:
                last_seen = 0

            current_videos = sorted((video for video in videos
                                     if video.vid > last_seen),
                                    key=lambda x: x.vid)
            to_delete = [video for video in videos if video.vid <= last_seen]
            for video in to_delete:
                logging.info('%r can be deleted' % (video,))
                downloader.delete_video(video)
            # all the others can be deleted
            for video in current_videos:
                downloader.fetch_video(video)
            # remove old videos that are not in the list
            playlist = '%s.xspf' % (show.nickname,)
            open(playlist, 'w').write(xspf.videos_to_xspf(current_videos))
            logging.info('generated %s' % (playlist,))

    elif command == 'seen':

        for show in shows:
            latest = max(v.vid for v in all_videos[show])
            parser.set('seen', show.nickname, str(latest))

        set_config(marker, parser)
        
