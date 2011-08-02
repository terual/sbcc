#!/usr/bin/env python
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

from os import path, devnull
from sys import exit, argv
from socket import error as socketerror
import logging
from subprocess import Popen

from pysqueezecenter.server import Server
from pysqueezecenter.player import Player
from urllib import unquote
from time import time 

import player
import setup
import functions

def main(sbs, sq, song):
    """
    Main loop where we are waiting for sbs.telnet.read_until
    and then parsing the output
    """
    try:
        current = []
        while True:
            state = unquote(sbs.telnet.read_until("\n"))
            state = functions.stripmac(state, config['mac'])
            logging.debug("TELNET: %s", state)

            if "open" in state:
                state = state.replace("open", "")
                state = state.strip()
                state = unquote( state.replace(config['remotefolder'], config['localfolder']) )

                state_time = functions.get_time_info(state)
                # telnet sends 'open' cmd twice, check for double
                if not state_time==current:
                    song.open(state_time)
                    current = state_time
                    logging.debug("Loaded song")

            elif "newsong" in state:
                logging.info("Start playback '%s - %s'", sq.get_track_artist(), sq.get_track_title())
                song.play()

            elif state=="pause 0":
                logging.info("Unpause")
                song.play()

            elif state=="pause 1":
                logging.info("Pause")
                song.pause()

            elif state=="stop":
                song.kill()

            elif "mixer volume" in state:
                state = state.replace("mixer volume", "")
                state = state.strip()
                logging.info("Change volume to %s percent", state)
                Popen(['amixer', 'set', 'Master', str(state)+"%"], stdout=nulfp.fileno())

            else:
                #telnet command which do not get interpreted
                pass

    except KeyboardInterrupt:
        logging.warning("Catched KeyboardInterrupt, exiting...")

    finally:
        song.kill()


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
    nulfp = open(devnull, "w")

    print "\nsbcc - SqueezeBox CopyCat version 0.5  Copyright (C) 2010 Bart Lauret"
    print "sbcc comes with ABSOLUTELY NO WARRANTY.  This is free software, and you are\nwelcome to redistribute it under certain conditions."
    print "Use the --daemon or -d option to start %s as a daemon.\n" % argv[0]

    # Check for neccesary bins
    if not functions.check_required():
        exit(1)

    # Configuration
    import ConfigParser
    config = {}
    
    loadconfig = ConfigParser.RawConfigParser(
        defaults={'host':'127.0.0.1',
                  'port':'9090',
                  'user':'',
                  'password':'',
                  'driver':'',
                  'output':'',
                  })
    
    logging.info("Path to config: " + path.dirname(argv[0]) + "/sbcc.cfg")
    loadconfig.read(path.dirname(argv[0]) + '/sbcc.cfg')

    try:
        for options in loadconfig.options('global'):                # creating dict of keys-values (why isn't this normally supported?)
            config[options] = loadconfig.get('global', options)
    except ConfigParser.NoSectionError:
        config = setup.setup()

    # Additional debugging info
    for key in config:
        logging.debug("%s: %s", key, config[key])


    # Connect to SBS
    sbs = Server(hostname=config['host'], 
                 port=config['port'], 
                 username=config['user'], 
                 password=config['passwd'] )

    # Check connection
    try:
        sbs.connect()
        if sbs.logged_in:
            logging.info("Connected to Squeezebox Server v%s on %s:%s", sbs.get_version(), config['host'], config['port'])
        else:
            logging.critical("Could not connect to server, possible wrong credentials")
            exit(1)
    except socketerror:
        logging.critical("Network is unreachable (check network connection and/or IP/port settings of your SB server)")
        p = Popen(["play", "noconnection.wav"])
        exit(1)

    # Additional info
    sq = sbs.get_player(config['mac'])
    logging.info("Copying behaviour of SB '%s'", sq.get_name())
    logging.info("Mode: %s | Time: %s | Connected: %s | WiFi: %s", 
                 sq.get_mode(), sq.get_time_elapsed(), 
                 sq.is_connected, sq.get_wifi_signal_strength())

    # Setting volume of alsa to volume of sb
    volume = sq.get_volume()
    Popen(['amixer', 'set', 'Master', str(volume)+"%"], stdout=nulfp.fileno())

    # All the magic: in this request we subscribe to all playlist events
    # and volume changes
    sbs.request("subscribe playlist%2Cmixer volume")

    # Initialise our song instance and go to main loop
    song = player.player(config['driver'], config['output'])
    main(sbs, sq, song)




