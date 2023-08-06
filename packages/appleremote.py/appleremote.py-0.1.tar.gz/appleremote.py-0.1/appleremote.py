#!/usr/bin/env python
# encoding: utf-8
#
# appleremote.py - A simple script to interface LIRC using the macmini 
# driver with MythTV running the remote control interface (enable in general 
# settings on the frontend). This has been tested on an AppleTV, but in theory 
# should work with any Intel Mac. Note this completely bypasses .lircrc; there 
# should be no mythtv entries in there. It just expects these commands in 
# lircd.conf (customise in the script if you want):
#
# play, up, down, prev, next, menu, repeat (optional for if you haven't 
# applied the LIRC repeat patch)
#
# Copyright (C) Ben Firshman 2008 
#
# This program is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the Free 
# Software Foundation; either version 2 of the License, or (at your option) 
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
#
# You should have received a copy of the GNU General Public License along with 
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple 
# Place, Suite 330, Boston, MA 02111-1307 USA

__version__ = 0.1

LIRC_PLAY   = "play"
LIRC_UP     = "up"
LIRC_DOWN   = "down"
LIRC_PREV   = "prev"
LIRC_NEXT   = "next"
LIRC_MENU   = "menu"
LIRC_REPEAT = "repeat"

LIRC_COMMANDS = [LIRC_PLAY, LIRC_UP, LIRC_DOWN, LIRC_PREV, LIRC_NEXT, 
                 LIRC_MENU]

import logging
import optparse
import os
import Queue
import socket
import sys
import time
import threading

class LircConnection(object):
    """A connection to LIRC"""
    def __init__(self, dev="/dev/lircd", poll=0.01):
        self.dev = dev
        self.poll = poll
        self.conn = None
        self.connected = False
        self.connect()
    
    def connect(self):
        """Connect to LIRC"""
        if self.connected:
            self.conn.close()
            self.connected = False
        try:
            self.conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.conn.connect(self.dev)
            self.conn.settimeout(self.poll)
            self.connected = True
        except socket.error, e:
            logging.warning("Could not connect to LIRC, retrying: %s" % e)
            time.sleep(0.5)
            return self.connect()
    
    def next_code(self):
        """Gets next command from LIRC"""
        try:
            buf = self.conn.recv(1024)
            if buf:
                try:
                    return buf.split()[2]
                except KeyError:
                    return None
            else:
                self.connect()
                return self.next_code()
        except socket.timeout:
            return None
        except socket.error, e:
            logging.warning("Error reading from LIRC, reconnecting: %s" % e)
            self.connect()
            return self.next_code()


class MythConnection(threading.Thread):
    """A connection to the MythTV frontend. Requires remote control enabled
    in general settings."""
    def __init__(self, host="localhost", port=6546, timeout=1):
        super(MythConnection, self).__init__(name="MythConnection")
        self.host = host
        self.port = port
        self.timeout = timeout # Time to wait for response from mythtv until 
                               # giving us. This will stop us lagging loads
        self.outq = Queue.Queue()
        self.inq = Queue.Queue()
        self.conn = None
        self.connected = False
        self.killed = False
        self.setDaemon(True)
        self.start()
    
    def die(self):
        self.killed = True
        self.q.put(None)
    
    def run(self):
        self.connect()
        while not self.killed:
            command = self.outq.get()
            if command:
                response = self._send_command(command)
                if response:
                    response = response.strip()
                    if response != "OK":
                        self.inq.put(response)
    
    def connect(self):
        if self.connected:
            self.conn.close()
            self.connected = False
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((self.host, self.port))
        except socket.error, e:
            logging.warning("Could not connect to myth, retrying: %s" % e)
            time.sleep(0.5)
            return self.connect()    
        try:
            self.conn.settimeout(0.2)
            while True:
                self.conn.recv(1024)
        except socket.timeout:
            self.conn.settimeout(self.timeout)
            self.connected = True
        except socket.error, e:
            logging.warning("Could not read from myth, reconnecting: %s" % e)
            time.sleep(0.5)
            return self.connect()
            
    def _send_command(self, command):
        """Send a command to mythtv"""
        try:
            self.conn.send(command+"\n")
            buf = self.conn.recv(1024).strip()
            if buf:
                if buf == "OK":
                    return None
                else:
                    return buf
            else:
                self.connect()
                return None
        except socket.timeout:
            return None
        except socket.error, e:
            logging.warning("Could not read from myth, reconnecting: %s" % e)
            self.connect()
            return None
    

class Code(object):
    """A unique remote code"""
    def __init__(self, name, myth, repeat_threshold=0.12):
        self.name = name
        self.myth = myth
        self.repeat_threshold = repeat_threshold
        self.last_time = 0
        self.repeat = 0
        
        self.first_done = False # Done intial action
        self.second_done = False # Done single secondary action
        self.next_second = 0 # Repeat number until a repeating secondary 
                              # action is done
    
    def _get_times(self):
        cur_time = time.time()
        return (cur_time, cur_time - self.last_time)
        
    def run(self):
        (cur_time, time_diff) = self._get_times()
        if time_diff < self.repeat_threshold:
            self.repeat += 1
            # Repeating secondary actions
            if self.next_second == self.repeat:
                if self.name == LIRC_UP or self.name == LIRC_DOWN :
                    self.myth.outq.put("key %s" % self.name)
                    self.next_second += 1
                elif self.name == LIRC_PREV:
                    self.myth.outq.put("key left")
                    self.next_second += 2
                elif self.name == LIRC_NEXT:
                    self.myth.outq.put("key right")
                    self.next_second += 2
            # Single secondary actions
            elif not self.second_done and self.repeat > 4:
                if self.name == LIRC_MENU:
                    self.myth.outq.put("key m")
                elif self.name == LIRC_PLAY:
                    self.myth.outq.put("key i")
                self.second_done = True
        else:
            self.repeat = 0
            self.first_done = False
            self.second_done = False
            self.next_second = 0
        logging.debug("name: %s" % self.name)
        logging.debug("time_diff: %s" % time_diff)
        logging.debug("repeat: %s" % self.repeat)
        logging.debug("next_second: %s" % self.next_second)
        self.last_time = cur_time
        self._clear_myth_queue()
    
    def check_single(self):
        if not self.first_done and self.repeat == 0 \
                and (self.name == LIRC_UP or self.name == LIRC_DOWN
                        or self.name == LIRC_PREV or self.name == LIRC_NEXT):
            # Immediate initial actions
            if self.name == LIRC_PREV:
                self.myth.outq.put("key left")
            elif self.name == LIRC_NEXT:
                self.myth.outq.put("key right")
            else:
                self.myth.outq.put("key %s" % self.name)
            self.next_second = 4
            self.first_done = True
        elif not self.first_done and self.repeat < 2:
            (cur_time, time_diff) = self._get_times()
            if time_diff >= self.repeat_threshold:
                # Delayed initial actions
                if self.name == LIRC_MENU:
                    self.myth.outq.put("key escape")
                elif self.name == LIRC_PLAY:
                    self.myth.outq.put("query location")
                    try:
                        loc = self.myth.inq.get(timeout=2).lower()
                    except Queue.Empty:
                        loc = ""
                    try:
                        if loc[0:8] == "playback":
                            self.myth.outq.put("key p")
                    except KeyError:
                        pass
                    self.myth.outq.put("key enter")
                self.first_done = True
        self._clear_myth_queue()
    
    def _clear_myth_queue(self):
        """Clear myth queue in case of previous timeouts"""
        while True:
            try:
                self.myth.inq.get(block=False)
            except Queue.Empty:
                break
    
    def __str__(self):
        return "%s, repeat %s" % (self.name, self.repeat)

def main():
    parser = optparse.OptionParser(version="%prog " + str(__version__))
    parser.set_defaults(
        repeat_threshold = 0.12,
        verbosity = 20,
        lirc_device = "/dev/lircd",
        myth_host = "localhost",
        myth_port = 6546)
    parser.add_option("-q", "--quiet", dest="verbosity",
                      action="store_const", const=40,
                      help="don't print anything except errors")
    parser.add_option("-v", "--verbose", dest="verbosity",
                      action="store_const", const=10,
                      help="print details on every keypress")
    parser.add_option("-d", "--lirc-device", dest="lirc_device",
                      help="device for connection to lirc, default: "
                      "/dev/lircd")
    parser.add_option("-m", "--myth-host", dest="myth_host",
                      help="host to connect to MythTV at, default: localhost")
    parser.add_option("-p", "--myth_port", dest="myth_port", type="int",
                      help="port to connect to MythTV at, default: 6546")
    parser.add_option("-t", "--repeat-threshold", dest="repeat_threshold",
                      help="maximum time in secs between LIRC key presses to "
                      "consider it a repeat from holding the button down, "
                      "default: 0.12", type="float")
    (options, args) = parser.parse_args()
    logging.root.setLevel(options.verbosity)
    lirc = LircConnection(options.lirc_device)
    myth = MythConnection(options.myth_host, options.myth_port)
    while not myth.connected:
        time.sleep(0.1)
    codes = {}
    for code in LIRC_COMMANDS:
        codes[code] = Code(code, myth, options.repeat_threshold)
    prev_code = None
    while True:
        code_name = lirc.next_code()
        if code_name:
            if code_name == LIRC_REPEAT:
                code_name = prev_code.name
            try:
                code = codes[code_name]
            except KeyError:
                logging.warning("Invalid code name receieved: %s" % code_name)
            code.run()
            prev_code = code
        elif prev_code:
            prev_code.check_single()

if __name__ == '__main__':
    sys.exit(main())

