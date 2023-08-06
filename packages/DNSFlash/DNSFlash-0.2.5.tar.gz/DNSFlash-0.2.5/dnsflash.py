#!/usr/bin/env python

###########################################################################
#   Copyright (C) 2008 by SukkoPera                                       #
#   sukkosoft@sukkology.net                                               #
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 2 of the License, or     #
#   (at your option) any later version.                                   #
#                                                                         #
#   This program is distributed in the hope that it will be useful,       #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#   GNU General Public License for more details.                          #
#                                                                         #
#   You should have received a copy of the GNU General Public License     #
#   along with this program; if not, write to the                         #
#   Free Software Foundation, Inc.,                                       #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
###########################################################################

# TODO Option to make the program silent if successful (i.e.: for crontab)
# TODO Option to specify a fixed IP address for the update.

import sys
# See if we can use syslog
try:
	import syslog
	haveSyslog = True
except NameError:
	haveSyslog = False
from optparse import OptionParser

from dnsomatic_api import DnsOMatic

PROGRAM_VERSION = "0.2.5"
CONFIG_FILE = "/etc/dnsomatic.conf"
#CONFIG_FILE = "dnsomatic.conf"


class _Actions:
	GETIP = 0
	UPDATE = 1

def getString (nodelist):
	"""Helper function to parse the XML configuration file."""
	if len (nodelist) >= 1 and nodelist[0].hasChildNodes ():
		ret = nodelist[0].childNodes[0].data.strip ()
	else:
		ret = None
	return ret

def getStringList (nodelist):
	"""Helper function to parse the XML configuration file."""
	ret = []
	for node in nodelist:
		ret.append (node.childNodes[0].data.strip ())
	return ret

def readConfig (configFile):
	"""Reads username and password from the configuration file."""
	from xml.dom.minidom import parse, parseString, getDOMImplementation

	try:
		dom = parse (configFile)
		for element in dom.getElementsByTagName ("config"):
			service = element.getAttribute ("service")
			if service == "dnsomatic":
				username = getString (element.getElementsByTagName ("username"))
				password = getString (element.getElementsByTagName ("password"))
				ip = getString (element.getElementsByTagName ("ip_address"))
				hostnames = getStringList (element.getElementsByTagName ("hostname"))
				break
	except IOError:
		# File not found
		print "Cannot open configuration file %s" % configFile
		username = None
		password = None
		ip = None
		hostnames = None
	return username, password, ip, hostnames

def getUsernameAndPassword (username_cmdline, password_cmdline, hostnames_cmdline, configfile):
	# Read username and password from configuration file, in case. The idea, here, is to use
	# values specified on the command line, filling in the missing ones with those taken from
	# the configuration file.
	if (username_cmdline is None or password_cmdline is None) and configfile != None:
		if configfile == '':
			configfile = CONFIG_FILE
		username_config, password_config, ip_config, hostnames_config = readConfig (configfile)

		if username_cmdline is None:
			username = username_config
		else:
			username = username_cmdline
		if password_cmdline is None:
			password = password_config
		else:
			password = password_cmdline
		if hostnames_cmdline is None:
			if hostnames_config is not None and len (hostnames_config) > 0:
				hostnames = hostnames_config
			else:
				hostnames = None
		else:
			hostnames = hostnames_cmdline
	else:
		# Both username and password provided on the command line (or configfile not specified),
		# no need to read configfile
		username = username_cmdline
		password = password_cmdline
		# If username and password are provided on the command line, we assume the hostlist will be as well
		hostnames = hostnames_cmdline
	
	return username, password, hostnames

class Logger:
	def __init__ (self, quiet, ident = None):
		if quiet:
			self.msg = self.quietprint
		else:
			self.msg = self.realprint

		if haveSyslog:
			syslog.openlog (ident, 0, syslog.LOG_USER)

	def __del__ (self):
		if haveSyslog:
			syslog.closelog ()

	def quietprint (self, msg):
		if haveSyslog:
			syslog.syslog (msg)
		pass

	def realprint (self, msg):
		print msg

	def err (self, msg):
		if haveSyslog:
			syslog.syslog (syslog.LOG_ERR, "ERROR: %s" % msg)
		print "ERROR: %s" % msg

def main ():
	cmdline_parser = OptionParser (usage = "Usage: %prog -G|-U [options]", description = "Update IP on the DNS-O-Matic service", version = "%s" % PROGRAM_VERSION)
	# Possible actions (i.e.: Operation modes)
	cmdline_parser.add_option ("-G", "--get", action = "store_const", dest = "action", const = _Actions.GETIP, help = "Retrieve the local IP", default = None)
	cmdline_parser.add_option ("-U", "--update", action = "store_const", dest = "action", const = _Actions.UPDATE, help = "Update the remote IP", default = None)
	# Other options
	cmdline_parser.add_option ("-u", "--username", action = "store", type = "string", dest = "username", help = "Specify username for DNS-O-Matic login (has precedence over configuration file)", default = None)
	cmdline_parser.add_option ("-p", "--password", action = "store", type = "string", dest = "password", help = "Specify password for DNS-O-Matic login", default = None)
	cmdline_parser.add_option ("-i", "--ip", action = "store", type = "string", dest = "ip", help = "Specify IP for update", default = None)
	cmdline_parser.add_option ("-c", "--configfile", action = "store", type = "string", dest = "configfile", help = "Read username and password from the specified file (Default: %s)" % CONFIG_FILE, default = CONFIG_FILE)
	cmdline_parser.add_option ("-H", "--hostname", action = "append", type = "string", dest = "hostnames", help = "Specify hostnames to update ", default = None)
	cmdline_parser.add_option ("-q", "--quiet", action = "store_true", dest = "quiet", help = "Only write to stdout in case of errors and log the rest to syslog (useful for crontab)", default = False)
	(options, args) = cmdline_parser.parse_args ()

	username, password, hostnames = getUsernameAndPassword (options.username, options.password, options.hostnames, options.configfile)

	# Init logger
	logger = Logger (options.quiet, "DNSFlash")

	# Proceed, according to the action
	if (options.action == None and ((username == None or username == '') or \
		(password == None or password == ''))) or \
		options.action == _Actions.GETIP:
		
		d = DnsOMatic ()
		ip = d.getCurrentLocalIP ()
		if ip != None:
			logger.msg ("Your IP is: %s" % ip)
			ret = 0
		else:
			logger.err ("Cannot retrieve IP")
			ret = 1
	elif options.action == _Actions.UPDATE or (options.action is None and ( \
		(username is not None and username != '') and \
		(password is not None and password != ''))):

		d = DnsOMatic (username, password)
		res = d.update (options.ip, hostnames)
		ret = 0		# Assume all went well
		if hostnames is None:
			(status, ip) = res[0]
			if status == "good":
				logger.msg ("All IPs successfully updated to %s" % ip)
			else:
				logger.err ("Cannot update any IP: %s" % status)
				ret = 1
		else:
			for hostname, (status, ip) in zip (hostnames, res):
				if status == "good":
					logger.msg ("IP for %s successfully updated to %s" % (hostname, ip))
				elif status == "alreadyok":
					logger.msg ("No need to update IP for %s, already pointing to %s" % (hostname, ip))
				else:
					logger.err ("Cannot update IP for %s: %s" % (hostname, status))
					ret += 1
	else:
		ret = 255
		return ret

# Go!
if __name__ == "__main__":
	sys.exit (main ())
