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
		PlayerBase.__init__(self, "Banshee", "1.5", "org.bansheeproject.Banshee")
	
	def is_playing(self):
		try:
			obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")		
			return str(obj.GetCurrentState()) == "playing"
		except:
			return
	
	def get_track(self):
		if not self.is_playing(): return
		
		try:
			obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
			data = obj.GetCurrentTrack()
		except:
			return
		
		if not "artist" in data.keys() or not "name" in data.keys() or not "album" in data.keys():
			return
		
		return {"artist": unicode(data["artist"]), "title": unicode(data["name"]), "album": unicode(data["album"]), 
				"uri": unicode(data["URI"])}
	
	def play_pause(self):
		try:
			obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
			obj.TogglePlaying()
		except:
			return
	
	def play(self):
		try:
			obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
			obj.Play()
		except:
			return
	
	def pause(self):
		try:
			obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
			obj.Pause()
		except:
			return
			
	def get_volume(self):
		try:
			obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
			return float(obj.GetVolume())
		except:
			return
	
	def set_volume(self, value):
		try:
			obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlayerEngine")
			obj.SetVolume(dbus.UInt16(value))
		except:
			return
	
	def next(self):
		try:
			obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlaybackController")
			obj.Next(False)
		except:
			return
	
	def previous(self):
		try:
			obj = self._get_dbus_object("/org/bansheeproject/Banshee/PlaybackController")		
			obj.Previous(False)
		except:
			return
