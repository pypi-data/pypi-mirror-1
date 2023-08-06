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
		PlayerBase.__init__(self, "Audacious", "1.5", "org.mpris.audacious")
		
	def get_track(self):
		try:
			object = self._get_dbus_object("/Player")
			metadata = object.GetMetadata()
		except:
			return
		
		if "artist" in metadata and "title" in metadata and "album" in metadata:
			return {"artist": unicode(metadata["artist"]), "title": unicode(metadata["title"]), "album": unicode(metadata["album"]), "uri": unicode(metadata["uri"])}
	
	def is_playing(self):
		try:
			object = self._get_dbus_object("/org/atheme/audacious")
			return str(object.Status()) == "playing"
		except:
			return
	
	def play_pause(self):
		try:
			object = self._get_dbus_object("/org/atheme/audacious")
			object.PlayPause()
		except:
			pass
		
	def play(self):
		try:
			object = self._get_dbus_object("/org/atheme/audacious")
			object.Play()
		except:
			pass

	def pause(self):
		try:
			object = self._get_dbus_object("/org/atheme/audacious")
			object.Pause()
		except:
			pass
	
	def next(self):
		try:
			object = self._get_dbus_object("/Player")
			object.Next()
		except:
			pass
	
	def previous(self):		
		try:
			object = self._get_dbus_object("/Player")
			object.Prev()
		except:
			return
	
	def get_volume(self):
		try:
			object = self._get_dbus_object("/org/atheme/audacious")
			return float(object.Volume()[0])
		except:
			return
	
	def set_volume(self, value):
		try:
			object = self._get_dbus_object("/org/atheme/audacious")
			object.SetVolume(value, value)
		except:
			return
