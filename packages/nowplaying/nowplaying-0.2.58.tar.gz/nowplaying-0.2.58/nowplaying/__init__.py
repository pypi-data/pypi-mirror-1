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

import dbus, imp, glob, os, sys

try:
    import mpd
except ImportError:
    mpd = None

import __mpd__, __mpris__

def _get_players():
    path = "/usr/share/python-nowplaying/players/"
    #path = "../players/"   # for debugging
    
    players = []
    for g in glob.glob(path + "*"):
        g = os.path.basename(g)
        
        if g.startswith("__"): continue
        
        name = g[:-3]
        data = imp.find_module(name, [path])
        module = imp.load_module(name, *data)
        players += [module.Player]
    
    return players

_defined_players = _get_players()

def _get_mpris_players():
    bus = dbus.SessionBus()
    
    players = []
    for name in bus.list_activatable_names():
        if name.startswith("org.mpris."):
            players.append(__mpris__.Player(name))
    
    return players

def _get_mpd_default():
    """ Returns a (hostname, port) from the environ variable if set """
    
    if not mpd:
        raise Exception("Could not find the module python-mpd")
    
    address = ["localhost", 6600]
    if "MPD_HOST" in os.environ.keys():
        address[0] = os.environ["MPD_HOST"]
    if "MPD_PORT" in os.environ.keys():
        address[1] = os.environ["MPD_PORT"]
    
    return address

_default_mpd = _get_mpd_default()

def get_mpd_player(host=_default_mpd[0], port=_default_mpd[1]):
    p = __mpd__.Player(host, port)
    
    if p.is_running():
        return p

def get_running_players():
    running = []
    for p in _defined_players:
        if p.is_running(): running += [p]
    
    mpd_player = get_mpd_player()
    if mpd_player:
        running += [mpd_player]
        
    return running + _get_mpris_players()

def get_player(player_id):
    """
        Returns a player object if the player's running
        None otherwise
    """
    
    for player in get_running_players():
        if player.get_id() == player_id:
            return player
