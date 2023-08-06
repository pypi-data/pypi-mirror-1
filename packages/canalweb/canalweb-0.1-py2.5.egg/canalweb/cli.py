#!/usr/bin/python

import logging
import optparse
import os
import sys

from canalweb import vod

def main():
    parser = optparse.OptionParser(
        usage='%prog [options] init | sync <show...> | list <show...>')
    parser.add_option('-c', '--cache',
                      action='store', dest='cache', default='.',
                      help='Directory in which to download files')

    (options, args) = parser.parse_args()

    # 'init': create the CANALWEB file
    # 'sync': download all files
    # 'list': list the available files
    if not args:
        parser.error('missing command')
    command = args.pop(0)

    logging.basicConfig(level=logging.DEBUG)

    cache = os.path.abspath(options.cache)
    marker = os.path.join(cache, 'CANALWEB')

    if command == 'init':
        logging.init('initializing new cache')
        if os.path.exists(marker):
            logging.error('directory already initialized')
            return 1
        open(marker, 'w').close()

    # sanity check: have a predefined file in the cache directory
    if not os.path.exists(marker):
        logging.error('invalid cache location %r: initialize it first' % (
            cache,))
        return 1

    if command not in ('list', 'sync'):
        parser.error('unknown command %r' % (command,))
        
    if not args:
        parser.error('missing show names')
        
    dl = vod.Downloader(cache)

    for show in args:
        vods = dl.get_video_info(show)

        if command == 'list':
            for video in vods:
                print video.date, video.url
        elif command == 'sync':
            for video in vods:
                dl.fetch_video(video)
