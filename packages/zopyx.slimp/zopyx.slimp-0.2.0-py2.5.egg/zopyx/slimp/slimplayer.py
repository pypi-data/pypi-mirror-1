#!/opt/python-2.4.3/bin/python
#-*- coding: iso-8859-15 -*-

""" Playlist feeder for a Slimp3 player """

import os 
import sys
import random
import time
from optparse import OptionParser
from zopyx.slimp import slimp


MAX_LENGTH_PLAYLIST = 40
mp3files = '/tmp/mp3files.txt'
random.seed(time.time()*os.getpid())

MP3FILES = []

def myrandom(max):
    return random.randint(0, max)

    s = ''.join([open('/dev/urandom').read(20) for i in range(100)])
    n = 0
    for c in s: n+=ord(c)
    return divmod(n, max) [1]

def rescan_mp3list(options):
    """ create a local cache file with the paths of all MP3 files """
    global MP3FILES

    if not os.path.exists(mp3files) or options.scanmp3:
        os.system('find %s -type d -exec chmod a+rx {} \;' % options.rootdir)
        os.system('find %s -type f -exec chmod a+r {} \;' % options.rootdir)
        os.system('/usr/bin/find %s -name \*mp3 |grep -vi badesalz|grep -v Suspektes |grep -v Texte >%s' % (options.rootdir, mp3files))

    MP3FILES = open(mp3files).readlines()


def choose_file(single=1):
    """ return a random sequence of MP3 files """

    item = MP3FILES[myrandom(len(MP3FILES))]
    if single:
        return [item]
    else:
        dirname = os.path.dirname(item)
        files = [os.path.join(dirname, f) for f in os.listdir(dirname) if f.endswith('.mp3') ]
        files.sort()
        return files

def files_for_playlist(slimp, options):

    if not os.path.exists(options.rootdir):
        raise ValueError, 'Directory "%s" does not exist' % options.rootdir

    if options.init: slimp.playlist_clear()
    current_track = int(slimp.playlist_tracknum())
    abc = int(slimp.playlist_numtracks())
    if abc - current_track > options.min_tracks: return []
    files = list()
    while len(files) < MAX_LENGTH_PLAYLIST:
        rnd = myrandom(100) # 10% for complete albums

        if rnd < 10:
            result = choose_file(single=0)
        else:
            result = choose_file(single=1)

        for f in result:
            if not f in files:
                files.append(f.strip())

    return files

def main():

    parser = OptionParser()
    parser.add_option('-d', '--rootdir', dest='rootdir', default='/raid/media2/media/mp3',
                     help='root directory')
    parser.add_option('-i', '--init-playlist', dest='init', action='store_true',
                     help='init the playlist')
    parser.add_option('-s', '--scan-mp3', dest='scanmp3', action='store_true',
                     help='rescan MP3 directory')
    parser.add_option('-n', '--min-tracks', dest='min_tracks', type='int',
                     help='minimal number of elements in playlist', default=5)
    options, args = parser.parse_args()

    slim = slimp.SLIM()
    rescan_mp3list(options)
    files = files_for_playlist(slim, options)
    slim.playlist_add(files)

    if files:
        current_track = int(slim.playlist_tracknum())
        for i in range(0, current_track): slim.playlist_delete(0)
        if options.init or not slim.playing(): 
            slim.shuffle(0)
            slim.play()
        slim.display('Playlist initialized', 'Have fun', 10)

if __name__ == '__main__':
    sys.exit(main())
