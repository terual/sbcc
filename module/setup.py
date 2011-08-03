# -*- coding: utf-8 -*-

"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.
    
"""

def setup():

    import sys
    from socket import error as socketerror
    import configparser
    from module.pysqueezecenter.server import Server
    from module.pysqueezecenter.player import Player
    # Python2 compatibility
    try:
        from urllib.parse import unquote
    except ImportError:
        from urllib import unquote

    print("No config file found, please provide the following details. The default is provided between brackets.")

    config = {}

    config['host'] = input("IP address of Squeezebox Server [127.0.0.1]: ")
    config['port'] = input("Port of Squeezebox Server [9090]: ")
    config['user'] = input("Username of server's CLI []: ")
    config['passwd'] = input("Password of server's CLI []: ")

    if not config['host']:
        config['host'] = "127.0.0.1"

    if not config['port']:
        config['port'] = "9090"

    sbs = Server(hostname=config['host'], 
                 port=config['port'], 
                 username=config['user'], 
                 password=config['passwd'] )

    print()
    try:
        sbs.connect()
        if sbs.logged_in:
            print("Succesfully connected to Squeezebox Server v%s on %s:%s" % ( sbs.get_version(), config['host'], config['port'] ))
        else:
            print("Could not connect to server, possible wrong credentials, run %s again" % sys.argv[0])
            sys.exit(1)
    except socketerror:
        print("Network is unreachable, check ip/port settings and run %s again." % sys.argv[0])
        sys.exit(1)

    print()
    print("The following players are connected to the server:")
    players = sbs.get_players()

    for i in range(len(players)):
        player = str(players[i]).replace("Player: ","")
        print("[%i]: %s" % (i+1, player))

    answer = int(input("Press the number which MAC address you want to use: "))-1
    config['mac'] = str(players[answer]).replace("Player: ","")

    print()
    sq = sbs.get_player(config['mac'])
    print("Path to current song in playlist, use this as a hint for the following question.")
    print(unquote(sq.get_track_path()))


    config['remotefolder'] = input("Remote folder where music resides on Squeezebox Server, e.g. file:///path/to/music []: ")
    config['localfolder'] = input("Local folder where music resides locally, e.g. /path/to/music []: ")
    config['driver'] = input("Music driver to use [alsa]: ")
    config['output'] = input("Audio device to use e.g.plughw:0,0 []: ")

    setupconfig = configparser.RawConfigParser()

    setupconfig.add_section('global')
    setupconfig.set('global', 'host', config['host'])
    setupconfig.set('global', 'port', config['port'])
    setupconfig.set('global', 'user', config['user'])
    setupconfig.set('global', 'passwd', config['passwd'])
    setupconfig.set('global', 'mac', config['mac'])
    setupconfig.set('global', 'remotefolder', config['remotefolder'])
    setupconfig.set('global', 'localfolder', config['localfolder'])
    setupconfig.set('global', 'driver', config['driver'])
    setupconfig.set('global', 'output', config['output'])


    with open('sbcc.cfg', 'wb') as configfile:
        setupconfig.write(configfile)

    print("Configuration is setup successfully!")

    return config

