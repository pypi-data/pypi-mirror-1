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

import urllib
import urllib2
import socket

# Maybe this could be turned to a base, service-independent class to be
# inheritedor to implement other similar services.
class DnsOMatic:
	"""Uses the DNS-o-matic API to update the IP address.
	Documentation about the DNS-O-Matic API is at https://www.dnsomatic.com/wiki/api.
	Be aware that nscd might cache DNS resolutions, rendering this program useless!
	"""
	version = "0.3.1"
	_updateUrl = "https://updates.dnsomatic.com"
	_defaultUrl = "%s/nic/update" % _updateUrl
	_defaultRealm = "DNSOMATIC"
	_getIpUrl = "http://myip.dnsomatic.com"
	_updateAllIPsKludge = "all.dnsomatic.com"
	_defaultUserAgent = "SukkoSoft - dnsomatic_api.py - %s" % version

	def __init__ (self, username = None, password = None, baseUrl = _defaultUrl, realm = _defaultRealm, userAgent = _defaultUserAgent):
		self._username = username
		self._password = password
		self._baseUrl = baseUrl
		self._realm = realm
		self._userAgent = userAgent
		self._setupHttp ()
		
	def _setupHttp (self):
		"""Sets up all things needed to use Basic HTTP Authentication."""
		if (1 and self._username is not None and self._username != '' and self._password is not None and self._password != ''):
			# Create an OpenerDirector with support for Basic HTTP Authentication
			passwdMan = urllib2.HTTPPasswordMgrWithDefaultRealm ()
			auth_handler = urllib2.HTTPBasicAuthHandler (passwdMan)
			auth_handler.add_password (None, self._updateUrl, self._username, self._password)
			self._httpOpener = urllib2.build_opener (auth_handler)
		else:
			# Use the default handler
			self._httpOpener = urllib2.build_opener ()

	def getCurrentLocalIP (self):
		"""Retrieve the current local IP through the DNS-O-Matic service."""
		f = self._httpOpener.open (self._getIpUrl)
		ip = "".join (f.readlines ()).strip ()
		return ip
	
	# This could be a static method, but it is not supported in Python 2.3 (which comes with Slackware 10.0)
	def getCurrentRemoteIP (self, hostname):
		"""Retrieve the IP the hostname we want to update currently points to."""
		try:
			# This has been converted to use getaddrinfo() to avoid problems with DNS
			# caching performed by nscd with gethostbyname() and other deprecated
			# functions. I'm just not sure it will always work with that [0][4][0] :D.
			#ip = socket.gethostbyname (hostname)
			sa = socket.getaddrinfo (hostname, None)
			ip = sa[0][4][0]
		except socket.gaierror:
			ip = None
		return ip

	def shouldUpdate (self, hostname, currentIP = None):
		if hostname is None:
			# No way to determine, so let's assume yes
			ret = True
		else:
			if currentIP is None:
				currentIP = self.getCurrentLocalIP ()
			desiredIP = self.getCurrentRemoteIP (hostname)
			if desiredIP is not None and currentIP == desiredIP:
				ret = False
			else:
				ret = True
		return ret

	def updateSingle (self, hostname = None, ip = None, force = False):
		"""Update a single address at the remote site."""
		if ip is None:
			# No IP to use for the update was specified. Get our
			# current IP automatically and use it.
			ip = self.getCurrentLocalIP ()
		if force or self.shouldUpdate (hostname, ip):
			# Either the IP to use for the update is different from
			# the one the hostname currently points to, or the user
			# wants to force the update, so let's go ahead.
			params = {"myip": ip}
			if hostname is not None:
				# Only update the requested service
				params["hostname"] = hostname
			headers = {"User-Agent": self._userAgent}
			enc_params = urllib.urlencode (params)
			if None:
				# This does NOT work, as it always updates *ALL* hosts.
				# Is there a problem with the code or does the site not handle
				# POST requests correctly?	
				req = urllib2.Request (self._baseUrl, enc_params, headers)
			else:
				# This works better
				url = "%s?%s" % (self._baseUrl, enc_params)
				req = urllib2.Request (url, headers = headers)
			try:
				f = self._httpOpener.open (req)
				result = "".join (f.readlines ()).strip ()
				#print result
				if result == "nohost":
					# No such host
					status = result
				else:
					status, ip = result.split ()
			except urllib2.HTTPError:
				status = "badauth"
				ip = "0.0.0.0"
			res = (status, ip)
		else:
			# Our local IP is already the same as the remote one
			res = ("alreadyok", ip)
		return res


	def update (self, ip = None, hostnames = None, force = False):
		"""Update several addresses to the same IP at the remote site."""
		if hostnames is None or len (hostnames) == 0:
			# Special case where we must update all the addresses
			res = self.updateSingle (ip = ip, force = force)
			ret = [res]
		else:
			# Update the requested addresses one by one
			ret = []
			for hostname in hostnames:
				res = self.updateSingle (hostname, ip, force)
				ret.append (res)
		return ret
