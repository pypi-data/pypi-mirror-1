#
# Copyright 2006 sense.lab e.V.
# 
# This file is part of the CryptoBox.
#
# The CryptoBox is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# The CryptoBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the CryptoBox; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""The network feature of the CryptoBox.

requires:
 - ifconfig
 - route
"""

__revision__ = "$Id"

import subprocess
import os
import cryptobox.plugins.base


## specify (in seconds), how long we should wait before redirecting and ip change
REDIRECT_DELAY = 10
CHANGE_IP_DELAY = 5 
## default network interface (if none is given via cryptobox.conf)
DEFAULT_INTERFACE = "eth0"

class network(cryptobox.plugins.base.CryptoBoxPlugin):
	"""The network feature of the CryptoBox.
	"""

	plugin_capabilities = [ "system" ]
	plugin_visibility = [ "preferences" ]
	request_auth = True
	rank = 30

	def do_action(self, store=None, redirected="", ip1="", ip2="", ip3="", ip4="",
			nm1="", nm2="", nm3="", nm4=""):
		"""Show a form containing the current IP - change it if requested.
		"""
		## if we were redirected, then we should display the default page
		self.cbox.log.debug("executing network plugin")
		if redirected == "1":
			self.cbox.log.debug("network plugin: redirected")
			return "form_network"
		## check possible actions
		if store is None:
			## no action was requested -> just show the form
			self.cbox.log.debug("network plugin: show form (interface %s)" \
					% self.__get_interface())
			self.__prepare_form_data()
			return "form_network"
		## change of ip address	and/or netmask requested
		elif store == "set_ip":
			self.cbox.log.debug("network plugin: changing server IP")
			if self.__IP_is_valid(ip1, ip2, ip3, ip4):
				new_ip = "%d.%d.%d.%d" % (int(ip1), int(ip2), int(ip3), int(ip4))
			else:
				self.hdf["Data.Warning"] = "Plugins.network.InvalidServerIP"
				self.__prepare_form_data()
				return "form_network"
			if self.__IP_is_valid(nm1, nm2, nm3, nm4):
				new_nm = "%d.%d.%d.%d" % (int(nm1), int(nm2), int(nm3), int(nm4))
			else:
				self.hdf["Data.Warning"] = "Plugins.network.InvalidNetmask"
				self.__prepare_form_data()
				return "form_network"
			if self.__set_ip(new_ip, new_nm):
				self.cbox.log.info("[network] the IP was successfully changed: %s" % new_ip)
				self.hdf["Data.Success"] = "Plugins.network.IPChanged"
				self.hdf["Data.Redirect.URL"] = self.__get_redirect_destination(new_ip)
				self.hdf["Data.Redirect.Delay"] = REDIRECT_DELAY
				self.prefs["_address"] = new_ip
				self.prefs["_netmask"] = new_nm
				try:
					self.cbox.prefs.plugin_conf.write()
				except IOError:
					self.cbox.log.warn("Could not write plugin configuration")
				self.__prepare_form_data()
				return "empty"
			else:
				self.cbox.log.warn("[network] failed to change IP address to: %s" % \
						new_ip)
				self.hdf["Data.Warning"] = "Plugins.network.AddressChangeFailed"
				self.__prepare_form_data()
				return "form_network"
		## request for default gateway change
		elif store == "set_gateway":
			old_gw = self.__get_current_gw()
			old_gw_str = ".".join([str(e) for e in old_gw])
			if self.__IP_is_valid(ip1, ip2, ip3, ip4):
				new_gw = (int(ip1), int(ip2), int(ip3), int(ip4))
				new_gw_str = ".".join([str(e) for e in new_gw])
			else:
				self.hdf["Data.Warning"] = "Plugins.network.InvalidGatewayIP"
				self.__prepare_form_data()
				return "form_network"
			if self.__set_gw(old_gw_str, new_gw_str):
				self.cbox.log.info( "[network] successfully changed gateway address:" \
						+ new_gw_str)
				self.hdf["Data.Success"] = "Plugins.network.GWChanged"
				self.prefs["_gateway"] = new_gw_str
				try:
					self.cbox.prefs.plugin_conf.write()
				except IOError:
					self.cbox.log.warn("Could not write plugin configuration")
			else:
				self.cbox.log.warn("[network] failed to change gateway address to: %s" \
						% new_gw_str)
				self.hdf["Data.Warning"] = "Plugins.network.GatewayChangeFailed"
			self.__prepare_form_data()
			return "form_network"
		else:
			## invalid action was requested -> show default form
			self.cbox.log.debug("network plugin: invalid request (%s)" % str(store))
			self.__prepare_form_data()
			return "form_network"


	def get_status(self):
		"""The current IP is the status of this feature.
		"""
		return "%d.%d.%d.%d" % self.__get_current_ip()


	def handle_event(self, event, event_info=None):
		"""Override bootup behaviour

		Apply the configured network settings
		"""
		if event == "bootup":
			if "_address" in self.prefs:
				if "_netmask" in self.prefs:
					self.__set_ip(self.prefs["_address"], self.prefs["_netmask"])
				else:
					## no netmask setting stored
					self.__set_ip(self.prefs["_address"])
			if "_gateway" in self.prefs:
				self.__set_gw(".".join([str(e) for e in self.__get_current_gw()]),
						self.prefs["_gateway"])


	def get_warnings(self):
		"""Check for missing programs
		"""
		warnings = []
		if not os.path.isfile(self.root_action.IFCONFIG_BIN):
			warnings.append((55, "Plugins.%s.MissingProgramIfconfig" % self.get_name()))
		if not os.path.isfile(self.root_action.ROUTE_BIN):
			warnings.append((52, "Plugins.%s.MissingProgramRoute" % self.get_name()))
		return warnings


	def __get_redirect_destination(self, ip):
		"""Put the new URL together.
		"""
		import cherrypy
		req = cherrypy.request
		base_parts = req.base.split(":")
		dest = "%s://%s" % (base_parts[0], ip)
		if len(base_parts) == 3:
			dest += ":%s" % base_parts[2]
		return dest


	def __prepare_form_data(self):
		"""Set some hdf values.
		"""
		#TODO: the following looks nicer in a loop
		(oc1, oc2, oc3, oc4) = self.__get_current_ip("ip")
		self.hdf[self.hdf_prefix + "ip.oc1"] = oc1
		self.hdf[self.hdf_prefix + "ip.oc2"] = oc2
		self.hdf[self.hdf_prefix + "ip.oc3"] = oc3
		self.hdf[self.hdf_prefix + "ip.oc4"] = oc4
		(oc1, oc2, oc3, oc4) = self.__get_current_ip("nm")
		self.hdf[self.hdf_prefix + "nm.oc1"] = oc1
		self.hdf[self.hdf_prefix + "nm.oc2"] = oc2
		self.hdf[self.hdf_prefix + "nm.oc3"] = oc3
		self.hdf[self.hdf_prefix + "nm.oc4"] = oc4
		(oc1, oc2, oc3, oc4) = self.__get_current_gw()
		self.hdf[self.hdf_prefix + "gw.oc1"] = oc1
		self.hdf[self.hdf_prefix + "gw.oc2"] = oc2
		self.hdf[self.hdf_prefix + "gw.oc3"] = oc3
		self.hdf[self.hdf_prefix + "gw.oc4"] = oc4


	def __get_current_ip(self, address_type="ip"):
		"""Retrieve the current IP.

		TODO: do not use "address_type" for ip and netmask, but return both in
		two tuples
		"""
		import re
		## get the current IP of the network interface
		proc = subprocess.Popen(
			shell = False,
			stdout = subprocess.PIPE,
			args = [
				self.root_action.IFCONFIG_BIN,
				self.__get_interface()])
		(stdout, stderr) = proc.communicate()
		if proc.returncode != 0:
			return (0, 0, 0, 0)
		if address_type == "ip":
			## this regex matches the four numbers of the IP
			match = re.search(r'inet [\w]+:(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\s', stdout)
			if match:
				## use the previously matched numbers
				return tuple([int(e) for e in match.groups()])
			else:
				return (0, 0, 0, 0)
		elif address_type == "nm":
			## this greps the netmask
			match = re.search(
					r'inet [\w]+:.*Mask:(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\s',
					stdout)
			if match:
				## use the previously matched numbers
				return tuple([int(e) for e in match.groups()])
			else:
				return (0, 0, 0, 0)


	def __get_current_gw(self):
		proc = subprocess.Popen(
			shell = False,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.root_action.ROUTE_BIN,
				"-n"])
		(stdout, stderr) = proc.communicate()
		if proc.returncode != 0:
			self.cbox.log.warn(
					"[network] failed to retrieve gateway address: %s" % stdout)
			return (0, 0, 0, 0)
		current_interface = self.__get_interface()
		## skip the first two heading lines
		for line in stdout.splitlines()[2:]:
			attrs = line.split()
			if len(attrs) != 8:
				self.cbox.log.info("[network] misformed route entry: %s" % line)
				continue
			interface = attrs[7]
			netmask = attrs[2]
			gateway = attrs[1]
			destination = attrs[0]
			if (destination == "0.0.0.0") and (netmask == "0.0.0.0") and \
					(interface == current_interface):
				gw_octet = tuple(gateway.split("."))
				if len(gw_octet) != 4:
					self.cbox.log.info(
							"[network] ignored invalid gateway setting: %s" % gateway)
				else:
					return gw_octet
		return (0, 0, 0, 0)


	def __set_ip(self, new_ip, new_nm="255.255.255.0"):
		"""Change the IP, additionally a netmask can be applied
		"""
		import threading
		## call the root_action script after some seconds - so we can deliver the page before
		def delayed_ip_change():
			"""A threaded function to change the IP.
			"""
			import time
			time.sleep(CHANGE_IP_DELAY)
			proc = subprocess.Popen(
				shell = False,
				stderr = subprocess.PIPE,
				args = [
					self.cbox.prefs["Programs"]["super"],
					self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
					"plugin",
					os.path.join(self.plugin_dir, "root_action.py"),
					"change_ip",
					self.__get_interface(),
					new_ip,
					new_nm])
			proc.wait()
			if proc.returncode != 0:
				self.cbox.log.warn("failed to change IP address: %s" % new_ip)
				self.cbox.log.warn("error output: %s" % str(proc.stderr.read()))
			return
		thread = threading.Thread()
		thread.run = delayed_ip_change
		thread.setDaemon(True)
		thread.start()
		# TODO: how could we guess, if it failed?
		return True
	

	def __set_gw(self, old_ip, new_ip):
		"""Change the gateway IP adress
		"""
		proc = subprocess.Popen(
			shell = False,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"plugin",
				os.path.join(self.plugin_dir, "root_action.py"),
				"change_gw",
				old_ip,
				new_ip])
		(output, error) = proc.communicate()
		if proc.returncode != 0:
			self.cbox.log.warn("[network] gateway setting failed: %s" % str(error))
			return False
		else:
			return True


	def __get_interface(self):
		"""Return the name of the configured network interface
		"""
		if "interface" in self.defaults:
			return self.defaults["interface"]
		else:
			return DEFAULT_INTERFACE


	def __IP_is_valid(self, ip1, ip2, ip3, ip4):
		try:
			for ip_in in (ip1, ip2, ip3, ip4):
				if (int(ip_in) < 0) or (int(ip_in) > 255):
					## we give an info only and a webwarning
					## further reaction depends on the case
					self.cbox.log.info("IP number is invalid: %s" % \
							str((ip1, ip2, ip3, ip4)))
					raise ValueError
		except ValueError:
			## handled by individual caller
			#self.hdf["Data.Warning"] = "Plugins.network.InvalidIP"
			return False
		return True

