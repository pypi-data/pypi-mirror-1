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
        DBusPlayer.__init__(self, "Exaile", "0.2", "org.exaile.DBusInterface")
    
    @silent
    def get_track(self):
        if not self.is_playing(): return
        
        obj = self._get_dbus_object("/DBusInterfaceObject")
        
        return {"artist": utf8(obj.get_artist()),
                "title": utf8(obj.get_title()),
                "album": utf8(obj.get_album()),
                "location": u""
                }
    
    @silent
    def is_playing(self):
        obj = self._get_dbus_object("/DBusInterfaceObject")
        
        return obj.query().startswith("status: playing")
    
    @silent
    def play_pause(self):
        obj = self._get_dbus_object("/DBusInterfaceObject")
        
        obj.play_pause()

    @silent
    def play(self):
        obj = self._get_dbus_object("/DBusInterfaceObject")
        obj.play()
    
    @silent
    def pause(self):
        obj = self._get_dbus_object("/DBusInterfaceObject")
        
        if self.is_playing():
            self.play_pause()
    
    @silent
    def next(self):
        obj = self._get_dbus_object("/DBusInterfaceObject")
        
        obj.next_track()
    
    @silent
    def previous(self):
        obj = self._get_dbus_object("/DBusInterfaceObject")
        
        obj.prev_track()
    
    @silent
    def get_volume(self):
        obj = self._get_dbus_object("/DBusInterfaceObject")
        
        return float(obj.get_volume())
    
    @silent
    def set_volume(self, value):
        obj = self._get_dbus_object("/DBusInterfaceObject")
        
        current = self.get_volume()
        
        value = float(value)
        
        if value < current:
            obj.decrease_volume(current - value)
        else:
            obj.increase_volume(value - current)
