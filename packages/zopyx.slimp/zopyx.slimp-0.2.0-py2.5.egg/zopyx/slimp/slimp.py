# -*- coding: iso-8859-15 -*-
 
import socket 
import urllib
import sys

HOST = 'localhost'
PORT = 9090

class SLIM(object):
    """ A Python interface for controlling the slimserver software from
        www.slimdevices.com.
    """

    def __init__(self, host=HOST, port=PORT):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect( (host, port))
        self.player_id = self.find_slimp()

    def find_slimp(self):
        count = int(self.request('player count ?').split()[-1])
        for i in range(count):
            model = self.request('player model %d ?' % i).split()[-1]
            if model == 'squeezebox2':
                id = self.request('player id %d ?' % i).split()[-1]
                return id

        raise RuntimError('No Squeezebox found')

    def __del__(self):
        self.s.send('exit\n')
        self.s.close()

    def request(self, cmd):
        if hasattr(self, 'player_id'):
            cmd = self.player_id + " " + cmd
        self.s.send(cmd + '\n')
        data = self.s.recv(8192)
        data = urllib.unquote(data)
        return data

    def volume(self, v='?'):
        return self.request('mixer volume %s' % v).split()[-1]

    def balance(self, v='?'):
        return self.request('mixer balance %s' % v).split()[-1]

    def base(self, v='?'):
        return self.request('mixer base %s' % v).split()[-1]

    def treble(self, v='?'):
        return self.request('mixer treble %s' % v).split()[-1]

    def display(self, t1, t2='', duration=15):
        t1 = urllib.quote(t1)
        t2 = urllib.quote(t2)
        return self.request('display %s %s %s' % (t1, t2, duration))

    def shuffle(self, mode=0):
        res = self.request('playlist shuffle %s' % mode)

    def playing(self):
        res = self.request('mode ?')
        if res.find('play') > -1: return 1
        else: return 0

    def play(self):
        return self.request('play')

    def stop(self):
        return self.request('stop')

    def pause(self):
        return self.request('pause 1')

    def unpause(self):
        return self.request('pause 0')

    def playlist_clear(self):
        return self.request('playlist clear')

    def playlist_add(self, files):
        for f in files:
            self.request('playlist add %s' % urllib.quote(f))

    def playlist_insert(self, files):
        for f in files:
            self.request('playlist insert %s' % urllib.quote(f))

    def playlist_delete(self, track):
        self.request('playlist delete %s' % track)

    def playlist_numtracks(self):
        return self.request('playlist tracks ?').split()[-1]

    def playlist_tracknum(self):
        return self.request('playlist index ?').split()[-1]

    def playlist_jump(self, to):
        return self.request('playlist index %s' % to)
        
if __name__ == '__main__':
    slimp = SLIMP3()
    print slimp.playlist_numtracks()
    print slimp.playlist_tracknum()
    print slimp.playing()

    slimp.display('Hello world', 'üöäÄÜßhello sucks', 10)
#    print slimp.volume()
#    slimp.volume(80)
