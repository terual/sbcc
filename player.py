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

import signal
import subprocess
import logging
from os import devnull
from time import time

class player:
    """
    player class which controls the decoding and playback of a file
    We use the flac decoder because of better results on some flacs
    """
    def __init__(self, driver, output):
        self.process_dec = None
        self.process = None
        self.play_pid = None
        self.dec_pid = None
        self.cmd = None
        self.nulfp = open(devnull, "w")
        self.driver = driver
        self.output = output

    def open(self, state):
        if state[1]:
            # Time information available, assuming image+cue
            if ".flac" in state[0]:
                self.cmd = ['flac', 
                            '-dcs', 
                            '--skip='+state[1].replace("0:", "", 1), 
                            '--until='+state[2].replace("0:", "", 1), 
                            state[0]]
            else:
                self.cmd = ['sox', 
                            '--no-show-progress', 
                            state[0], 
                            'trim', state[1], state[3], 
                            '--type', 'wav', 
                            '-' ]
        else:
            if ".flac" in state[0]:
                self.cmd = ['flac', 
                            '-dcs', 
                            state[0]]
            elif ".mp3" in state[0]:
                self.cmd = ['lame', 
                            '--decode', 
                            '--silent', 
                            state[0], 
                            '-']
            else:
                self.cmd = ['sox', 
                            '--no-show-progress', 
                            state[0], 
                            '--type', 'wav', 
                            '-' ]

        

        self.process_dec = subprocess.Popen(self.cmd, 
                                            stdout=subprocess.PIPE, 
                                            stderr=self.nulfp.fileno() )
        self.dec_pid = self.process_dec.pid
        logging.debug("Decoding process PID %s started: %s", self.process_dec.pid, self.cmd)

        self.process = subprocess.Popen(['play', 
                                         '--no-show-progress', 
                                         '--type', 'wav', 
                                         '-'], 
                                        stdin=self.process_dec.stdout, 
                                        stderr=self.nulfp.fileno() )
        self.play_pid = self.process.pid
        logging.debug("Play process PID %s started", self.process.pid)

        """
        non working for 24-bit (pulse??)
        self.process = subprocess.Popen(['aplay', 
                                          '-D', 'default', 
                                          '--quiet', 
                                          '-t', 'wav', 
                                          '-'], stdin=self.process_dec.stdout)
        """

        self.process_dec.send_signal(signal.SIGSTOP)
        logging.debug("Decoding process paused and waiting for cue")

        if not self.process_dec.poll()==None:
            logging.error("Error in decoding process, return code %s", self.process_dec.poll())

    def play(self):
        if self.play_pid:
            self.process_dec.send_signal(signal.SIGCONT)

    def pause(self):
        if self.play_pid:
            self.process_dec.send_signal(signal.SIGSTOP)

    def kill(self):
        if self.play_pid:
            try:
                self.process.kill()
                logging.debug("Stopping play process PID %s", self.play_pid)
                self.play_pid = None
            except Exception:
                logging.debug("No play process to kill")

        if self.dec_pid:
            try:
                self.process_dec.kill()
                logging.debug("Stopping decoding process PID %s", self.dec_pid)
                self.dec_pid = None
            except Exception:
                logging.debug("No decoding process to kill")


