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
	
	def __init__(self, dbus_name):
		
		identity = dbus.SessionBus().get_object(dbus_name, "/").Identity().split(" ")
		
		PlayerBase.__init__(self, identity[0], identity[1], dbus_name)
	
	@silent
	def get_track(self):
		if not self.is_playing(): return

		metadata = self._get_dbus_object("/Player").GetMetadata()
		
		track = {}
		for key in metadata:
			track[utf8(key)] = utf8(metadata[key])
		
		return track
	
	@silent
	def is_playing(self):
		return self._get_dbus_object("/Player").GetStatus()[0] == 0
	
	@silent
	def play_pause(self):
		self._get_dbus_object("/Player").Pause()
	
	@silent
	def play(self):
		if not self.is_playing():
			self.play_pause()
	
	@silent
	def pause(self):
		if self.is_playing():
			self.play_pause()
	
	@silent
	def next(self):
		self._get_dbus_object("/Player").Next()
	
	@silent
	def previous(self):
		self._get_dbus_object("/Player").Prev()
	
	@silent
	def get_volume(self):
		return float(self._get_dbus_object("/Player").VolumeGet())
	
	@silent
	def set_volume(self, value):		
		self._get_dbus_object("/Player").VolumeSet(int(value))
