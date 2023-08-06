#	
#	Copyright 2009 Amr Hassan <amr.hassan@gmail.com>
#	
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 2 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program; if not, write to the Free Software
#	Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#	MA 02110-1301, USA.

from __base__ import *

class Player(PlayerBase):
	
	def __init__(self):
		PlayerBase.__init__(self, "Exaile", "org.exaile.DBusInterface")
	
	def get_track(self):
		try:
			obj = self._get_dbus_object("/DBusInterfaceObject")
		except:
			return
		
		return {"artist": unicode(obj.get_artist()),
				"title": unicode(obj.get_title()),
				"album": unicode(obj.get_album()),
				"uri": u""
				}
	
	def is_playing(self):
		try:
			obj = self._get_dbus_object("/DBusInterfaceObject")
		except:
			return
		
		return obj.query().startswith("status: playing")
	
	def play_pause(self):
		try:
			obj = self._get_dbus_object("/DBusInterfaceObject")
		except:
			return
		
		obj.play_pause()
	
	def next(self):
		try:
			obj = self._get_dbus_object("/DBusInterfaceObject")
		except:
			return
		
		obj.next_track()
	
	def previous(self):
		try:
			obj = self._get_dbus_object("/DBusInterfaceObject")
		except:
			return
		
		obj.prev_track()
	
	def get_volume(self):
		try:
			obj = self._get_dbus_object("/DBusInterfaceObject")
		except:
			return
		
		return float(obj.get_volume())
	
	def set_volume(self, value):
		try:
			obj = self._get_dbus_object("/DBusInterfaceObject")
		except:
			return
		
		current = self.get_volume()
		
		if value < current:
			obj.decrease_volume(current - value)
		else:
			obj.increase_volume(value - current)
	
