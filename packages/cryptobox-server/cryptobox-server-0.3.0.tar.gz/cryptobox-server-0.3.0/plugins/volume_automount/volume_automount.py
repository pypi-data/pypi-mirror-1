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

__revision__ = "$Id"

import cryptobox.plugins.base
import cryptobox.core.container
from cryptobox.core.exceptions import *


class volume_automount(cryptobox.plugins.base.CryptoBoxPlugin):

	plugin_capabilities = [ "volume" ]
	plugin_visibility = [ "properties" ]
	request_auth = False
	rank = 80

	true_string = "yes"
	false_string = "no"


	def do_action(self, action=None):
		container = self.cbox.get_container(self.device)
		if action is None:
			pass
		elif action == "enable":
			self.__set_auto_mount(container, True)
			self.hdf["Data.Success"] = "Plugins.volume_automount.AutoMountEnabled"
			self.cbox.log.info("volume_automount: enabled for device '%s'" % self.device)
		elif action == "disable":
			self.__set_auto_mount(container, False)
			self.hdf["Data.Success"] = "Plugins.volume_automount.AutoMountDisabled"
			self.cbox.log.info("volume_automount: disabled for device '%s'" % self.device)
		else:
			self.cbox.log.info("volume_automount: invalid action (%s)" % str(action))
		self.__prepare_hdf()
		return "volume_automount"
	

	def handle_event(self, event, event_info=None):
		"""Override bootup behaviour.
		
		Mount all volumes marked as 'automount'.
		"""
		cryptobox.plugins.base.CryptoBoxPlugin.handle_event(self, event, event_info)
		if event == "bootup":
			for cont in self.cbox.get_container_list():
				if self.__is_auto_mount(cont) and not cont.is_mounted():
					cont.mount()
	

	def is_useful(self, device):
		"""Automount does not work for encrypted volumes.
		"""
		cont = self.cbox.get_container(device)
		if not cont:
			return False
		if cont.get_type() != cryptobox.core.container.CONTAINERTYPES["luks"]:
			return True
		return False


	def get_status(self):
		return str(self.__is_auto_mount(self.cbox.get_container(self.device)))
	

	def __prepare_hdf(self):
		if self.__is_auto_mount(self.cbox.get_container(self.device)):
			self.hdf[self.hdf_prefix + "automount_setting"] = "1"
		else:
			self.hdf[self.hdf_prefix + "automount_setting"] = "0"


	def __is_auto_mount(self, container):
		if not container:
			return False
		## only valid for plain volumes
		if container.get_type() != cryptobox.core.container.CONTAINERTYPES["plain"]:
			return False
		if "_automount_names" in self.prefs:
			if container.get_name() in self.prefs["_automount_names"]:
				return True
			else:
				return False
		else:
			return False
	

	def __set_auto_mount(self, container, state):
		if state == self.__is_auto_mount(container):
			return
		name = container.get_name()
		if not "_automount_names" in self.prefs:
			self.prefs["_automount_names"] = []
		if state:
			self.prefs["_automount_names"].append(name)
		else:
			self.prefs["_automount_names"].remove(name)
		try:
			self.cbox.prefs.plugin_conf.write()
		except IOError:
			self.cbox.log.warn("Failed to store plugin configuration")

