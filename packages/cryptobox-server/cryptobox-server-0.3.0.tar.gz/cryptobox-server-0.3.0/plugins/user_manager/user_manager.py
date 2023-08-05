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

RESERVED_USERS = [ "admin" ]

class user_manager(cryptobox.plugins.base.CryptoBoxPlugin):

	plugin_capabilities = [ "system" ]
	plugin_visibility = [ "preferences" ]
	request_auth = True
	rank = 45

	def do_action(self, store=None, user=None, new_pw=None, new_pw2=None):
		import re
		admin_dict = self.cbox.prefs.user_db["admins"]
		self.__clean_hdf()
		if store is None:
			pass
		elif store == "add_user":
			if (user is None) or (re.search(r'\W', user)):
				self.hdf["Data.Warning"] = "Plugins.user_manager.InvalidUserName"
			elif not new_pw:
				self.hdf["Data.Warning"] = "EmptyNewPassword"
			elif new_pw != new_pw2:
				self.hdf["Data.Warning"] = "DifferentPasswords"
			elif user in admin_dict.keys():
				self.hdf["Data.Warning"] = "Plugins.user_manager.UserAlreadyExists"
			else:
				admin_dict[user] = self.cbox.prefs.user_db.get_digest(new_pw)
				self.hdf["Data.Success"] = "Plugins.user_manager.UserAdded"
				try:
					self.cbox.prefs.user_db.write()
				except IOError:
					self.cbox.log.warn("failed to write user database")
		elif store == "change_password":
			if not new_pw:
				self.hdf["Data.Warning"] = "EmptyNewPassword"
			elif new_pw != new_pw2:
				self.hdf["Data.Warning"] = "DifferentPasswords"
			elif user in admin_dict.keys():
				admin_dict[user] = self.cbox.prefs.user_db.get_digest(new_pw)
				self.hdf["Data.Success"] = "Plugins.user_manager.PasswordChanged"
				try:
					self.cbox.prefs.user_db.write()
				except IOError:
					self.cbox.log.warn("failed to write user database")
			else:
				self.cbox.log.info("user_manager: invalid user choosen (%s)" % str(user))
		elif store == "del_user":
			if user in RESERVED_USERS:
				self.cbox.log.info("user_manager: tried to remove reserved user (%s)" % user)
				self.hdf["Data.Warning"] = "NeverRemoveReservedUser"
			elif user in admin_dict.keys():
				del admin_dict[user]
				self.hdf["Data.Success"] = "Plugins.user_manager.UserRemoved"
				try:
					self.cbox.prefs.user_db.write()
				except IOError:
					self.cbox.log.warn("failed to write user database")
			else:
				self.cbox.log.info("user_manager: tried to remove non-existing user (%s)" \
						% str(user))
		else:
			self.cbox.log.info("user_manager: invalid value of 'store' (%s)" % store)
		self.__prepare_hdf(admin_dict)
		return "user_list"


	def get_status(self):
		return ":".join(self.cbox.prefs.user_db["admins"].keys())


	def __clean_hdf(self):
		for key in self.hdf.keys():
			del self.hdf[key]


	def __prepare_hdf(self, dataset):
		## sort by name
		users = dataset.keys()
		users.sort()
		## export all users
		for name in users:
			self.hdf[self.hdf_prefix + "Users." + name] = name

