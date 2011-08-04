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

import logging
from subprocess import Popen
from os import devnull
try:
    from functools import reduce
except:
    pass

def get_time_info(state):
    if "#" in state:
        state,time = state.split("#")
        begin,end = time.split("-")
        length = float(end)-float(begin)
        end = float(end)
        begin = float(begin)
        newstate = [state, 
                    float(begin), 
                    float(end), 
                    float(length)]
    else:
        newstate = [state, float(0), float(0), float(0)]

    return newstate


def stripmac(state,mac):
    if mac in state:
        state = state.replace(mac, "")
        state = state.strip()

        if "playlist" in state:
            state = state.replace("playlist", "")
            state = state.strip()
    else:
        logging.error("MAC address not in telnet comm: %s", state)
    return state

def check_required():
    nulfp = open(devnull, "w")

    for bin in ['sox', 'flac', 'lame', 'play', 'amixer']:
        check = Popen(['which', bin], stdout=nulfp.fileno(), stderr=nulfp.fileno()).wait()
        if not check==0:
            logging.critical("Neccesary %s program not found on your system", bin)
            return False
    return True

def flac_time(t):
    # adapted from Paul McGuire 
    # http://stackoverflow.com/questions/1384406/python-convert-seconds-to-hhmmss
    # flac wants mm:ss.ms
    return "%02d:%02d.%03d" % \
        reduce(lambda ll,b : divmod(ll[0],b) + ll[1:], 
            [(t*1000,), 1000, 60])

def sox_time(t):
    # idem as flac_time
    # but sox wants hh:mm:ss.ms
    return "%02d:%02d:%02d.%03d" % \
        reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
            [(t*1000,),1000,60,60])


