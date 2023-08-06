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


import os
import sys
# See if we can use syslog
try:
	import syslog
	haveSyslog = True
except NameError:
	haveSyslog = False
from optparse import OptionParser
from xml.dom.minidom import parse, parseString, getDOMImplementation

from dnsomatic_api import DnsOMatic

PROGRAM_VERSION = "0.3.1"
DEFAULT_CONFIG_FILE = "/etc/dnsflash.conf"

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
	"""Read username, password and other data from configuration file."""
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

def actionGetIP (logger):
	d = DnsOMatic ()
	ip = d.getCurrentLocalIP ()
	if ip is not None:
		logger.msg ("Your IP is: %s" % ip)
		ret = 0
	else:
		logger.err ("Cannot retrieve IP")
		ret = 1
	return ret

def actionUpdateIP (logger, cmd_username = None, cmd_password = None, cmd_ip = None, cmd_hostnames = None, config = None, force = False):
	if config is not None:
		#print "Using configuration file: %s" % config
		username, password, ip, hostnames = readConfig (config)
		ret = 0
	else:
		if cmd_username is None or cmd_username == "":
			logger.err ("No username provided")
			ret = 101
		elif cmd_password is None or cmd_password == "":
			logger.err ("No password provided")
			ret = 102
		else:
			username = cmd_username
			password = cmd_password
			ip = cmd_ip
			hostnames = cmd_hostnames
			ret = 0

	if ret == 0:
		d = DnsOMatic (username, password)
		res = d.update (ip, hostnames, force)
		if hostnames is None or len (hostnames) == 0:
			(status, ip) = res[0]
			if status == "good":
				logger.msg ("All IPs successfully updated to %s" % ip)
			else:
				logger.err ("Cannot update any IP: %s" % status)
				ret = 1
		else:
			ret = 0		# Assume all went well
			assert (len (hostnames) == len (res))
			for hostname, (status, ip) in zip (hostnames, res):
				if status == "good":
					logger.msg ("IP for %s successfully updated to %s" % (hostname, ip))
				elif status == "alreadyok":
					logger.msg ("No need to update IP for %s, already pointing to %s" % (hostname, ip))
				else:
					logger.err ("Cannot update IP for %s: %s" % (hostname, status))
					ret += 1
	return ret

def main ():
	cmdline_parser = OptionParser (usage = "Usage: %prog -g [options]", description = "Update IP on the DNS-O-Matic service", version = "%s" % PROGRAM_VERSION)
	cmdline_parser.add_option ("-g", "--getip", action = "store_true", dest = "no_update", help = "Do not update anything, only retrieve the local IP", default = False)
	cmdline_parser.add_option ("-u", "--username", action = "store", type = "string", dest = "username", help = "Specify username for DNS-O-Matic login (has precedence over configuration file)", default = None)
	cmdline_parser.add_option ("-p", "--password", action = "store", type = "string", dest = "password", help = "Specify password for DNS-O-Matic login", default = None)
	cmdline_parser.add_option ("-i", "--ip", action = "store", type = "string", dest = "ip", help = "Specify IP for update", default = None)
	cmdline_parser.add_option ("-c", "--configfile", action = "store", type = "string", dest = "configfile", help = "Read username and password from the specified file (Default: %s)" % DEFAULT_CONFIG_FILE, default = None)
	cmdline_parser.add_option ("-n", "--hostname", action = "append", type = "string", dest = "hostnames", help = "Hostname to update (Might be used multiple times)", metavar = "HOSTNAME", default = None)
	cmdline_parser.add_option ("-f", "--force", action = "store_true", dest = "force", help = "Force IP update, even if the hostname already points to the requeste IP address (Warning: might result in ban!)", default = False)
	cmdline_parser.add_option ("-q", "--quiet", action = "store_true", dest = "quiet", help = "Only write to stdout in case of errors and log the rest to syslog (useful for crontab)", default = False)
	(options, args) = cmdline_parser.parse_args ()

	# Init logger
	logger = Logger (options.quiet, "DNSFlash")

	# Proceed, according to the action
	if not options.no_update:
		if options.configfile is not None:
			# User has specified a configfile, use it
			ret = actionUpdateIP (logger, config = options.configfile, force = options.force)
		elif options.username is not None and options.password is not None:
			# No configfile specified, but we have a username and password, so use these
			ret = actionUpdateIP (logger, options.username, options.password, options.ip, options.hostnames, force = options.force)
		elif os.path.isfile (DEFAULT_CONFIG_FILE):
			# No configfile, nor username/password specified, but there is a system-wide configfile, so use this
			ret = actionUpdateIP (logger, config = DEFAULT_CONFIG_FILE, force = options.force)
		else:
			# No configfile at all, nor username/password specified, so just get the local IP
			ret = actionGetIP (logger)
	else:
			# User only wants the current IP
			ret = actionGetIP (logger)
	return ret

# Go!
if __name__ == "__main__":
	sys.exit (main ())
