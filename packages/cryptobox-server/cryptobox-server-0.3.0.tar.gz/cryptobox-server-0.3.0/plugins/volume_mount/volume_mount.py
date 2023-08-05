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
from cryptobox.core.exceptions import *
import cryptobox.core.container as cbxContainer


class volume_mount(cryptobox.plugins.base.CryptoBoxPlugin):

	plugin_capabilities = [ "volume" ]
	plugin_visibility = [ "volume" ]
	request_auth = False
	rank = 0


	def do_action(self, action=None, pw=None):
		self.hdf[self.hdf_prefix + "PluginDir"] = self.plugin_dir
		self.container = self.cbox.get_container(self.device)
		if action == "mount_plain":
			return self.__do_mount_plain()
		elif action == "mount_luks":
			return self.__do_mount_luks(pw)
		elif action == "umount":
			return self.__do_umount()
		elif not action:
			return "volume_status"
		else:
			self.cbox.log.info("plugin 'volume_mount' - unknown action: %s" % action)
			return "volume_status"
	

	def get_status(self):
		container = self.cbox.get_container(self.device)
		if not self.container:
			return "invalid device"
		if container.is_mounted():
			return "active"
		else:
			return "passive"


	def __do_mount_plain(self):
		if self.container.is_mounted():
			self.hdf["Data.Warning"] = "Plugins.volume_mount.IsAlreadyMounted"
			self.cbox.log.info("the device (%s) is already mounted" % self.device)
			return "volume_status"
		if self.container.get_type() != cbxContainer.CONTAINERTYPES["plain"]:
			## not a plain container
			self.cbox.log.info("plugin 'volume_mount' - invalid container type")
			self.hdf["Data.Warning"] = "Plugins.volume_mount.InvalidContainerType"
			return "volume_status"
		try:
			self.container.mount()
		except CBMountError, err_msg:
			self.hdf["Data.Warning"] = "Plugins.volume_mount.MountFailed"
			self.cbox.log.warn("failed to mount the device (%s): %s" \
					% (self.device, err_msg))
			return "volume_status"
		except CBContainerError, err_msg:
			self.hdf["Data.Warning"] = "Plugins.volume_mount.MountFailed"
			self.cbox.log.warn("failed to mount the device (%s): %s" \
					% (self.device, err_msg))
			return "volume_status"
		self.cbox.log.info("successfully mounted the volume: %s" % self.device)
		self.hdf["Data.Success"] = "Plugins.volume_mount.MountDone"
		return "volume_status"


	def __do_mount_luks(self, pw):
		if self.container.get_type() != cbxContainer.CONTAINERTYPES["luks"]:
			## not a luks container - fail silently
			self.cbox.log.info("plugin 'volume_mount' - invalid container type")
			return "volume_status"
		if self.container.is_mounted():
			self.hdf["Data.Warning"] = "Plugins.volume_mount.IsAlreadyMounted"
			self.cbox.log.info("the device (%s) is already mounted" % self.device)
			return "volume_status"
		if not pw:
			self.hdf["Data.Warning"] = "EmptyPassword"
			self.cbox.log.info("no password was supplied for mounting of device: '%s'" \
					% self.device)
			return "volume_status"
		try:
			self.container.mount(pw)
		except CBMountError, err_msg:
			self.hdf["Data.Warning"] = "Plugins.volume_mount.MountCryptoFailed"
			self.cbox.log.warn("failed to mount the device (%s): %s" \
					% (self.device, err_msg))
			return "volume_status"
		except CBContainerError, err_msg:
			self.hdf["Data.Warning"] = "Plugins.volume_mount.MountCryptoFailed"
			self.cbox.log.warn("failed to mount the device (%s): %s" \
					% (self.device, err_msg))
			return "volume_status"
		self.cbox.log.info("successfully mounted the volume: %s" % self.device)
		self.hdf["Data.Success"] = "Plugins.volume_mount.MountDone"
		return "volume_status"


	def __do_umount(self):
		if not self.container.is_mounted():
			self.hdf["Data.Warning"] = "Plugins.volume_mount.IsNotMounted"
			self.cbox.log.info("the device (%s) is currently not mounted" % self.device)
			return "volume_status"
		try:
			self.container.umount()
		except CBUmountError, err_msg:
			self.hdf["Data.Warning"] = "UmountFailed"
			self.cbox.log.warn("could not umount the volume (%s): %s" \
					% (self.device, err_msg))
			return "volume_status"
		self.cbox.log.info("successfully unmounted the container: %s" % self.device)
		self.hdf["Data.Success"] = "Plugins.volume_mount.UmountDone"
		return "volume_status"

