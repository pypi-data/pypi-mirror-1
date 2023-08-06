#    
#    Copyright 2009 Amr Hassan <amr.hassan@gmail.com>
#    
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#    MA 02110-1301, USA.

from base import *

try:
    import mpd
except ImportError:
    mpd = None

class Player(PlayerBase):
    
    def __init__(self, host, port):
        
        PlayerBase.__init__(self, "MPD", host + ":" + str(port))
        self.client = mpd.MPDClient()
        
        try:
            self.client.connect(host, port)
        except:
            self.client = None
    
    def get_track(self):
        if not self.is_playing(): return
        
        metadata = self.client.currentsong()
        
        return {"artist": utf8(metadata["artist"]),
                "title": utf8(metadata["title"]),
                "album": utf8(metadata["album"]),
                "location": ""
                }
    
    def is_running(self):
        return bool(self.client)
    
    def is_playing(self):
        return self.client.status()["state"] == "play"
    
    def play_pause(self):
        self.client.pause()
    
    def play(self):
        self.client.play()
    
    def pause(self):
        self.client.pause(1)
    
    def next(self):
        self.client.next()
    
    def previous(self):
        self.client.previous()
    
    def get_volume(self):
        return self.client.status()["volume"]
    
    def set_volume(self, value):
        self.client.setvol(value)
