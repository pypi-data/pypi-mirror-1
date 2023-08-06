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

import dbus

def utf8(string):
    if type(string) == unicode:
        return string
    else:
        try:
            return unicode(string, "utf-8")
        except TypeError:
            return unicode(string)

class PlayerBase(object):
    """A base for player objects"""
    
    def __init__(self, name, version):
        (self.name, self.version) = (name, version)

    def __repr__(self):
        return self.get_name()
    
    def __hash__(self):
        return hash(self.get_id())
    
    def get_track(self):
        return NotImplemented
    
    def get_name(self):
        return self.name
    
    def is_running(self):
        return NotImplemented
    
    def is_playing(self):
        return NotImplemented
    
    def play_pause(self):
        pass
    
    def play(self):
        pass
    
    def pause(self):
        pass
    
    def next(self):
        pass
    
    def previous(self):
        pass
    
    def get_volume(self):
        return NotImplemented
    
    def set_volume(self, value):
        pass
    
    def get_id(self):
        return "%s_%s" %(self.name.lower(), utf8(self.version).replace(".", "_"))
        
    def get_snapshot(self):
        """Returns a snapshots of all the values of this player."""
        
        return {"volume": self.get_volume(),
                "track": self.get_track(),
                "name": self.name,
                "version": self.version,
                "is_playing": self.is_playing(),
                "player_id": self.get_id(),
                }

class DBusPlayer(PlayerBase):
    """ A DBus player """
    
    def __init__(self, name, version, dbus_name):
        PlayerBase.__init__(self, name, version)
        
        self.dbus_name = dbus_name
        self.bus = dbus.SessionBus()
    
    def _get_dbus_object(self, path):
        return self.bus.get_object(self.dbus_name, path)
    
    def is_running(self):
        return self.dbus_name in self.bus.list_activatable_names()


def silent(funct):
    """a descriptor"""
    
    def r(*args):
        try:
            return funct(*args)
        except:
            return None
    
    return r
