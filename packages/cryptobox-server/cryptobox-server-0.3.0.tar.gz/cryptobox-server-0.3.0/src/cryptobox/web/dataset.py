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

"""Manage the hdf dataset of the cryptobox web sites.
"""

__revision__ = "$Id"

import os
import cryptobox.core.container as cbxContainer
import cryptobox.core.tools as cbxTools


class WebInterfaceDataset(dict):
	"""this class contains all data that should be available for the clearsilver
	templates
	"""

	def __init__(self, cbox, prefs, plugin_manager):
		super(WebInterfaceDataset, self).__init__()
		self.prefs = prefs
		self.cbox = cbox
		self.__set_config_values()
		self.plugin_manager = plugin_manager
		self.set_crypto_box_state()
		self.set_plugin_data()
		self.set_containers_state()


	def set_crypto_box_state(self):
		"""Set some hdf values according to the cryptobox as a whole.
		"""
		import cherrypy
		import cryptobox.core.main
		import cryptobox.web.languages
		import cryptobox
		self["Data.Version"] = cryptobox.__version__
		## first: clean the dataset up - necessary if we were called more than once
		for key in self.keys():
			if key.startswith("Data.Languages."):
				del self[key]
		langs = self.cbox.prefs["WebSettings"]["Languages"][:]
		langs.sort()
		for (index, lang) in enumerate(langs):
			try:
				(langname, plural_info) = cryptobox.web.languages.LANGUAGE_INFO[lang]
				self["Data.Languages.%d.link" % index] = langname
				self["Data.Languages.%d.name" % index] = lang
				self.cbox.log.info("language loaded: %s" % lang)
			except KeyError:
				## language was not found
				self.cbox.log.warn(
						"invalid language specified in configuration: %s" % lang)

		## check the help setting
		try:
			if cherrypy.request.params["help"] == "1":
				self["Settings.Help"] = "1"
				self["Settings.LinkAttrs.help"] = "1"
		except (AttributeError, KeyError):
			## no setting or first start before request
			## reset values - just in case we are called more than once
			self["Settings.Help"] = "0"
			if "Settings.LinkAttrs.help" in self:
				del self["Settings.LinkAttrs.help"]

		try:
			self["Data.ScriptURL.Prot"] = cherrypy.request.scheme
			host = cherrypy.request.headers["Host"]
			self["Data.ScriptURL.Host"] = host.split(":", 1)[0]
			complete_url = "%s://%s" % \
					(self["Data.ScriptURL.Prot"], self["Data.ScriptURL.Host"])
			try:
				port = int(host.split(":", 1)[1])
				complete_url += ":%s" % port
			except (IndexError, ValueError):
				if cherrypy.request.scheme == "http":
					port = 80
				elif cherrypy.request.scheme == "https":
					port = 443
				else:
					## unknown scheme -> port 0
					self.cbox.log.info("unknown protocol scheme used: %s" % \
							(cherrypy.request.scheme,))
					port = 0
			self["Data.ScriptURL.Port"] = port
			## retrieve the relative address of the CGI (or the cherrypy base address)
			## remove the last part of the url and add a slash
			path = "/".join(cherrypy.request.path.split("/")[:-1]) + "/"
			self["Data.ScriptURL.Path"] = path
			complete_url += path
			self["Data.ScriptURL"] = complete_url
			for (key, value) in cherrypy.request.params.items():
				if isinstance(value, list):
					self["Data.ScriptParams.%s" % key] = value[0]
				else:
					self["Data.ScriptParams.%s" % key] = str(value)
			if cherrypy.request.headers.has_key("CRYPTOBOX-Location"):
				self.cbox.log.debug("ProxyLocation: %s" % \
						cherrypy.request.headers["CRYPTOBOX-Location"])
				self["Data.Proxy.ScriptPath"] = \
						cherrypy.request.headers["CRYPTOBOX-Location"]
			if cherrypy.request.headers.has_key("X-Forwarded-Host"):
				self.cbox.log.debug("ProxyHost: %s" % cherrypy.request.headers["X-Forwarded-Host"])
				self["Data.Proxy.Host"] = cherrypy.request.headers["X-Forwarded-Host"]
		except AttributeError:
			self["Data.ScriptURL"] = ""


	def set_current_disk_state(self, device):
		"""Set some hdf values according to the currently active disk.
		"""
		for container in self.cbox.get_container_list():
			if container.get_device() == device:
				is_encrypted = (container.get_type() == \
						cbxContainer.CONTAINERTYPES["luks"]) and 1 or 0
				is_plain = (container.get_type() == \
						cbxContainer.CONTAINERTYPES["plain"]) and 1 or 0
				is_mounted = container.is_mounted() and 1 or 0
				is_busy = container.is_busy() and 1 or 0
				self["Data.CurrentDisk.device"] = container.get_device()
				self["Data.CurrentDisk.name"] = container.get_name()
				self["Data.CurrentDisk.encryption"] = is_encrypted
				self["Data.CurrentDisk.plaintext"] = is_plain
				self["Data.CurrentDisk.active"] = is_mounted
				self["Data.CurrentDisk.busy"] = is_busy
				self["Data.CurrentDisk.size"] = cbxTools.get_blockdevice_size_humanly(
						container.get_device())
				if is_mounted:
					self.cbox.log.debug("Retrieving container's data: %s" % \
							container.get_name())
					(size, avail, used) = container.get_capacity()
					percent = int(used)*100 / int(size)
					self.cbox.log.debug(percent)
					self["Data.CurrentDisk.capacity.used"] = used
					self["Data.CurrentDisk.capacity.free"] = avail
					self["Data.CurrentDisk.capacity.size"] = size
					self["Data.CurrentDisk.capacity.percent"] = percent
				else:
					for key in self.keys():
						if key.startswith("Data.CurrentDisk.capacity."):
							del self[key]
		self["Settings.LinkAttrs.device"] = device
	

	def set_containers_state(self):
		"""Set some hdf values according to the list of available containers.
		"""
		## first: clean the dataset up - necessary if we were called more than once
		for key in self.keys():
			if key.startswith("Data.Disks."):
				del self[key]
		avail_counter  = 0
		active_counter = 0
		self.cbox.reread_container_list()
		for container in self.cbox.get_container_list():
			## useful if the container was changed during an action
			container.reset_object()
			is_encrypted = (container.get_type() == \
					cbxContainer.CONTAINERTYPES["luks"]) and 1 or 0
			is_plain = (container.get_type() == \
					cbxContainer.CONTAINERTYPES["plain"]) and 1 or 0
			is_mounted = container.is_mounted() and 1 or 0
			is_busy = container.is_busy() and 1 or 0
			self["Data.Disks.%d.device" % avail_counter] = container.get_device()
			self["Data.Disks.%d.name" % avail_counter] = container.get_name()
			self["Data.Disks.%d.encryption" % avail_counter] = is_encrypted
			self["Data.Disks.%d.plaintext" % avail_counter] = is_plain
			self["Data.Disks.%d.busy" % avail_counter] = is_busy 
			self["Data.Disks.%d.active" % avail_counter] = is_mounted
			self["Data.Disks.%d.size" % avail_counter] = \
					cbxTools.get_blockdevice_size_humanly(container.get_device())
			if is_mounted:
				active_counter += 1
			avail_counter += 1
		self["Data.activeDisksCount"] = active_counter
	

	def set_plugin_data(self):
		"""Set some hdf values according to the available features.
		"""
		## first: clean the dataset up - necessary if we were called more than once
		for key in self.keys():
			if key.startswith("Settings.PluginList."):
				del self[key]
		for plugin in self.plugin_manager.get_plugins():
			entry_name = "Settings.PluginList." + plugin.get_name()
			self[entry_name] = plugin.get_name()
			self[entry_name + ".Rank"] = plugin.get_rank()
			self[entry_name + ".RequestAuth"] = plugin.is_auth_required() and "1" or "0"
			for capy in plugin.plugin_capabilities:
				self[entry_name + ".Types." + capy] = "1"
			for visi in plugin.get_visibility():
				self[entry_name + ".Visible." + visi] = "1"


	def __set_config_values(self):
		"""Set some hdf values according to configuration settings.
		"""
		self["Settings.TemplateDir"] = os.path.abspath(
				self.prefs["Locations"]["TemplateDir"])
		self["Settings.DocDir"] = os.path.abspath(self.prefs["Locations"]["DocDir"])
		self["Settings.Stylesheet"] = self.prefs["WebSettings"]["Stylesheet"]
		self["Settings.Language"] = self.prefs["WebSettings"]["Languages"][0]
		self["Settings.SettingsDir"] = self.prefs["Locations"]["SettingsDir"]

