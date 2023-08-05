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
import cryptobox.core.container as cbx_container

## map filesystem types to the appropriate arguments for 'mkfs'
FSTYPES = {
	"windows": "vfat",
	"linux": "ext3" }


class volume_format_fs(cryptobox.plugins.base.CryptoBoxPlugin):

	plugin_capabilities = [ "volume" ]
	plugin_visibility = [ "volume" ]
	request_auth = True
	rank = 60


	def do_action(self, store=None, fs_type="windows", container_type="luks",
			crypto_password=None, crypto_password2=None, confirm=None):
		container = self.cbox.get_container(self.device)
		## exit immediately if the device is not writeable
		if not container.is_writeable():
			self.hdf["Data.Warning"] = "DeviceNotWriteable"
			return "empty"
		if not fs_type in FSTYPES.keys():
			self.cbox.log.info("Invalid filesystem type choosen: %s" % str(fs_type))
			return "volume_format"
		self.hdf[self.hdf_prefix + "fs_type"] = fs_type
		if not container_type in ['plain', 'luks']:
			self.cbox.log.info("Invalid container type type choosen: %s" % \
					str(container_type))
			return "volume_format"
		self.hdf[self.hdf_prefix + "container_type"] = container_type
		for t in FSTYPES.keys():
			self.hdf[self.hdf_prefix + "fs_types." + t] = t
		if store == "step1":
			if not confirm:
				self.cbox.log.info("Missing confirmation for formatting of " + \
						"filesystem: %s" % self.device)
				self.hdf["Data.Warning"] = "Plugins.volume_format_fs.FormatNotConfirmed"
				return "volume_format"
			if container_type == "luks":
				return "volume_format_luks"
			elif container_type == "plain":
				return self.__format_plain(FSTYPES[fs_type])
		elif store == "step2":
			if container_type == "luks":
				return self.__format_luks(FSTYPES[fs_type],
						crypto_password, crypto_password2)
			else:
				self.cbox.log.info("Invalid input value for 'container_type': %s" \
						% container_type)
				return "volume_format"
		elif store:
			self.cbox.log.info("Invalid input value for 'store': %s" % store)
			return "volume_format"
		else:
			return "volume_format"


	def get_status(self):
		return "no status"


	def __format_plain(self, fs_type):
		try:
			container = self.cbox.get_container(self.device)
			container.create(cbx_container.CONTAINERTYPES["plain"], fs_type=fs_type)
		except CBVolumeIsActive:
			self.hdf["Data.Warning"] = "VolumeMayNotBeMounted"
			self.cbox.log.info("Initialization is not possible as long as the device " \
					+ "(%s) is mounted" % self.device)
			return "volume_format"
		except CBContainerError, err_msg:
			self.hdf["Data.Warning"] = "Plugins.volume_format_fs.FormatFailed"
			self.cbox.log.error("Initialization of the device (%s) failed: %s" % \
					(self.device, err_msg))
			return "volume_format"
		else:
			self.hdf["Data.Success"] = "Plugins.volume_format_fs.FormatSuccess"
			self.cbox.log.info("Successfully initialized device '%s'" % self.device)
			return { "plugin":"disks", "values":{} }


	def __format_luks(self, fs_type, pw, pw2):
		if not pw:
			self.hdf["Data.Warning"] = "EmptyPassword"
			self.cbox.log.info("No crypto password was supplied for initialization " \
					+ "of device '%s'" % self.device)
			return "volume_format"
		if pw != pw2:
			self.hdf["Data.Warning"] = "DifferentPasswords"
			self.cbox.log.info("The crypto password was not repeated correctly for " \
					+ "initialization of device '%s'" % self.device)
			return "volume_format"
		container = self.cbox.get_container(self.device)
		try:
			container.create(cbx_container.CONTAINERTYPES["luks"],
					fs_type=fs_type, password=pw)
		except CBVolumeIsActive:
			self.hdf["Data.Warning"] = "VolumeMayNotBeMounted"
			self.cbox.log.info("Initialization is not possible as long as the device " \
					+ "(%s) is mounted" % self.device)
			return "volume_format"
		except CBContainerError, err_msg:
			self.hdf["Data.Warning"] = "Plugins.volume_format_fs.FormatFailed"
			self.cbox.log.error("Initialization of the device (%s) failed: %s" % \
					(self.device, err_msg))
			return "volume_format"
		else:
			self.hdf["Data.Success"] = "Plugins.volume_format_fs.FormatSuccess"
			self.cbox.log.info("Successfully initialized device '%s'" % self.device)
			return { "plugin":"disks", "values":{} }

