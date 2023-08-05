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


class volume_rename(cryptobox.plugins.base.CryptoBoxPlugin):

	plugin_capabilities = [ "volume" ]
	plugin_visibility = [ "properties" ]
	request_auth = False
	rank = 60


	def do_action(self, store=None, vol_name=None):
		self.container = self.cbox.get_container(self.device)
		if not self.container:
			return None
		self.__prepare_hdf()
		if store and vol_name:
			return self.__set_volume_name(vol_name)
		else:
			return "volume_rename"
	

	def get_status(self):
		self.container = self.cbox.get_container(self.device)
		if not self.container:
			return "invalid device"
		return "%s" % self.container.get_name()
	

	def __prepare_hdf(self):
		self.hdf[self.hdf_prefix + "vol_name"] = self.container.get_name()
	

	def __set_volume_name(self, vol_name):
		if vol_name == self.container.get_name():
			## nothing has to be done
			return "volume_rename"
		try:
			self.container.set_name(vol_name)
			self.hdf["Data.Success"] = "Plugins.volume_rename.VolumeNameChanged"
		except CBVolumeIsActive:
			self.hdf["Data.Warning"] = "Plugins.volume_rename.NoRenameIfActive"
		except CBInvalidName:
			self.hdf["Data.Warning"] = "Plugins.volume_rename.InvalidVolumeName"
		except CBNameIsInUse:
			self.hdf["Data.Warning"] = "Plugins.volume_rename.VolumeNameIsInUse"
		except CBContainerError:
			self.hdf["Data.Warning"] = "Plugins.volume_rename.SetVolumeNameFailed"
		## reread the volume name
		self.__prepare_hdf()
		return "volume_rename"

