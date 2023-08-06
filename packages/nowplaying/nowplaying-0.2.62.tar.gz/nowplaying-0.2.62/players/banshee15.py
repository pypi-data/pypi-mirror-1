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


from np.base import *

class Player(DBusPlayer):
    
    def __init__(self):
        DBusPlayer.__init__(self, "Banshee", "1.5", "org.bansheeproject.Banshee")
    
    @silent
    def is_playing(self):
        obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")        
        return str(obj.GetCurrentState()) == "playing"
    
    @silent
    def get_track(self):
        if not self.is_playing(): return
        
        obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
        data = obj.GetCurrentTrack()
        
        if not "artist" in data.keys() or not "name" in data.keys() or not "album" in data.keys():
            return
        
        return {"artist": utf8(data["artist"]), "title": utf8(data["name"]), "album": utf8(data["album"]), 
                "location": utf8(data["URI"])}
    
    @silent
    def play_pause(self):
        obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
        obj.TogglePlaying()
    
    @silent
    def play(self):
        obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
        obj.Play()
    
    @silent
    def pause(self):
        obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
        obj.Pause()
    
    @silent
    def get_volume(self):
        obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
        return float(obj.GetVolume())
    
    @silent
    def set_volume(self, value):
        obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
        obj.SetVolume(dbus.UInt16(value))
    
    @silent
    def next(self):
        obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlaybackController")
        obj.Next(False)
    
    @silent
    def previous(self):
        obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlaybackController")        
        obj.Previous(False)
