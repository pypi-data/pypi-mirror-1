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

import dbus
import imp
import glob
import os
import sys

import nowplaying.players

import dbus
import nowplaying.players.__mpris__

def _get_players():
	players_path = nowplaying.players.__path__[0]
	
	players = []
	
	for path in glob.glob(players_path + "/*.py"):
		
		name = os.path.basename(path)[:-3]
		if name.startswith("__"): continue
		
		full_name = "%s.players.%s" %(__package__, name)
		
		if not full_name in sys.modules.keys():
			imp.load_module(full_name, *imp.find_module(name, [players_path]))
		
		players.append(sys.modules[full_name].Player())
	
	return players

def _get_mpris_players():
	bus = dbus.SessionBus()
	
	players = []
	for name in bus.list_activatable_names():
		if name.startswith("org.mpris."):
			players.append(nowplaying.players.__mpris__.Player(name))
	
	return players

_players = _get_players()

def get_running_players():
	running = []
	for p in _players:
		if p.is_running():
			running.append(p)
	
	return running + _get_mpris_players()

def get_player(player_id):
	"""
		Returns a player object if the player's running
		None otherwise
	"""
	
	for player in get_running_players():
		if player.get_id() == player_id:
			return player
