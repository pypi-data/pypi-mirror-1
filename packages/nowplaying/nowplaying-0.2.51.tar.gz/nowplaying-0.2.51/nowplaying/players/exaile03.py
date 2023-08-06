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
		PlayerBase.__init__(self, "Exaile", "0.3", "org.exaile.Exaile")
	
	def get_track(self):
		if not self.is_playing(): return
		
		try:
			obj = self._get_dbus_object("/org/exaile/Exaile")
		except:
			return
		
		return {"artist": utf8(obj.GetTrackAttr("artist")),
				"title": utf8(obj.GetTrackAttr("title")),
				"album": utf8(obj.GetTrackAttr("album")),
				"uri": utf8(obj.GetTrackAttr("__loc")),
				"bitrate": utf8(obj.GetTrackAttr("__bitrate")),
				"length": utf8(obj.GetTrackAttr("__length")),
				"number": utf8(obj.GetTrackAttr("tracknumber")),
				"playcount": utf8(obj.GetTrackAttr("__playcount")),
				}
	
	def is_playing(self):
		try:
			obj = self._get_dbus_object("/org/exaile/Exaile")
		except:
			return
		
		return obj.Query().startswith("status: playing")
	
	def play_pause(self):
		try:
			obj = self._get_dbus_object("/org/exaile/Exaile")
		except:
			return
		
		obj.PlayPause()

	def play(self):
		try:
			obj = self._get_dbus_object("/org/exaile/Exaile")
		except:
			return
		
		obj.Play()

	def pause(self):
		try:
			obj = self._get_dbus_object("/org/exaile/Exaile")
		except:
			return
		
		if self.is_playing():
			obj.PlayPause()
		
	def next(self):
		try:
			obj = self._get_dbus_object("/org/exaile/Exaile")
		except:
			return
		
		obj.Next()
	
	def previous(self):
		try:
			obj = self._get_dbus_object("/org/exaile/Exaile")
		except:
			return
		
		obj.Prev()
	
	def get_volume(self):
		try:
			obj = self._get_dbus_object("/org/exaile/Exaile")
		except:
			return
		
		return float(obj.GetVolume())
	
	def set_volume(self, value):
		try:
			obj = self._get_dbus_object("/org/exaile/Exaile")
		except:
			return
		
		obj.ChangeVolume(int(value))
	
