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


class volume_chpasswd(cryptobox.plugins.base.CryptoBoxPlugin):

	plugin_capabilities = [ "volume" ]
	plugin_visibility = [ "properties" ]
	request_auth = False
	rank = 70


	def do_action(self, store=None, old_pw=None, new_pw=None, new_pw2=None):
		self.container = self.cbox.get_container(self.device)
		if not self.container:
			return None
		elif store == "change_pw":
			return self.__change_password(old_pw, new_pw, new_pw2)
		elif not store:
			return "volume_chpasswd"
		else:
			self.cbox.log.info("plugin 'volume_chpasswd' - unknown action: %s" % store)
			return "volume_chpasswd"
	

	def get_status(self):
		return "TODO"

	
	def is_useful(self, device):
		from cryptobox.core.container import CONTAINERTYPES as cont_types
		cont = self.cbox.get_container(device)
		if not cont:
			return False
		if cont.get_type() == cont_types["luks"]:
			return True
		return False
	

	def __change_password(self, old_pw, new_pw, new_pw2):
		if not old_pw:
			self.hdf["Data.Warning"] = "EmptyPassword"
		elif not new_pw:
			self.hdf["Data.Warning"] = "EmptyNewPassword"
		elif new_pw != new_pw2:
			self.hdf["Data.Warning"] = "DifferentPasswords"
		elif old_pw == new_pw:
			## do nothing
			pass
		else:
			try:
				self.container.change_password(old_pw, new_pw)
			except CBInvalidType, err_msg:
				self.cbox.log.info("plugin 'volume_chpasswd' - cannot change " \
						+ "passphrase for non-encrypted container (%s): %s" \
						% (self.device, err_msg))
			except CBVolumeIsActive:
				self.hdf["Data.Warning"] = "VolumeMayNotBeMounted"
			except CBChangePasswordError, err_msg:
				self.cbox.log.warn("plugin 'volume_chpasswd' - cannot change " \
						+ "password for device (%s): %s" % (self.device, err_msg))
				self.hdf["Data.Warning"] = "Plugins.volume_chpasswd.PasswordChange"
			else:
				self.hdf["Data.Success"] = "Plugins.volume_chpasswd.PasswordChange"
		return "volume_chpasswd"

