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

from cryptobox.tests.base import WebInterfaceTestClass

## this user may not be removed
from user_manager import RESERVED_USERS

class unittests(WebInterfaceTestClass):
	

	def test_read_users(self):
		"""does the 'admin' user exist?"""
		cur_users = self._getUsers()
		self.cmd.find("Add new user")
		self.assertTrue("admin" in cur_users)


	def test_test_wrong_credentials(self):
		"""check if the user_manager is protected"""
		url = self.url + "user_manager"
		self.register_auth(url,"foo","bar")
		self.cmd.go(url)
		self.cmd.notfind("Manage users")
	

	def test_add_existing_user(self):
		"""adding an existing user should fail"""
		url = self.url + "user_manager"
		self.register_auth(url)
		self._add_user("admin","foo","foo")
		self.cmd.find("The choosen username does already exist")


	def test_add_invalid_username(self):
		"""adding an invalid username should fail"""
		url = self.url + "user_manager"
		self.register_auth(url)
		self._add_user("foo/bar","foo","foo")
		self.cmd.find("Invalid username")
		self.assertFalse("foo/bar" in self._getUsers())


	def test_add_without_password(self):
		"""adding a user without password should fail"""
		url = self.url + "user_manager"
		self.register_auth(url)
		self.assertFalse("foo" in self._getUsers())
		self._add_user("foo","","foo")
		self.cmd.find("Missing new password")
		self.assertFalse("foo" in self._getUsers())


	def test_add_with_different_passwords(self):
		"""adding a user with different passwords should fail"""
		url = self.url + "user_manager"
		self.register_auth(url)
		self.assertFalse("foo" in self._getUsers())
		self._add_user("foo","bar","foo")
		self.cmd.find("Different passwords")
		self.assertFalse("foo" in self._getUsers())


	def test_change_pw_for_invalid_user(self):
		"""changing a password of a non existing user should fail"""
		url = self.url + "user_manager"
		self.register_auth(url)
		self.assertFalse("barfoo" in self._getUsers())
		self.cmd.go(url + "?store=change_password&user=foobar&new_pw=foo&new_pw2=foo")
		self.cmd.notfind("Password changed")


	def test_change_pw_without_password(self):
		"""changing a password without a new password should fail"""
		url = self.url + "user_manager"
		self.register_auth(url)
		self.assertFalse("foo" in self._getUsers())
		self._add_user("foo","bar","bar")
		self.assertTrue("foo" in self._getUsers())
		self._change_password("foo","","foo")
		self.cmd.find("Missing new password")
		self._del_user("foo")
		self.assertFalse("foo" in self._getUsers())


	def test_change_pw_wit_different_passwords(self):
		"""changing a password while supplying different passwords should fail"""
		url = self.url + "user_manager"
		self.register_auth(url)
		self.assertFalse("foo" in self._getUsers())
		self._add_user("foo","bar","bar")
		self.assertTrue("foo" in self._getUsers())
		self._change_password("foo","bar","foo")
		self.cmd.find("Different passwords")
		self._del_user("foo")
		self.assertFalse("foo" in self._getUsers())


	def _remove_reserved_user(self):
		"""removing a reserved user should fail"""
		url = self.url + "user_manager"
		self.register_auth(url)
		self.assertTrue("admin" in self._getUsers())
		self._del_user("admin")
		self.cmd.find("may not remove a reserved user")
		self.assertTrue("admin" in self._getUsers())


	def _remove_non_existing_user(self):
		"""removing a non-existing user should fail"""
		url = self.url + "user_manager"
		self.register_auth(url)
		self.assertFalse("barfoo" in self._getUsers())
		self._del_user("barfoo")
		self.cmd.notfind("User removed")


	def test_manage_users(self):
		"""add a new user, change its password and remove the user afterwards"""
		url = self.url + "user_manager"
		self.register_auth(url)
		## remove the user that should be added - just in case a previous run was unclean
		## check its existence before
		if "foobar" in self._getUsers(): self._del_user("foobar")
		## add a new user
		self._add_user("foobar","foo","foo")
		self.cmd.find("User added")
		users = self._getUsers()
		self.assertTrue("foobar" in users)
		## change the password of the new user
		self.register_auth(url,"foobar","foo")
		self._change_password("foobar","bar","bar")
		self.cmd.find("Password changed")
		## remove the new user
		self.register_auth(url,"foobar","bar")
		self._del_user("foobar")
		self.cmd.find("User removed")
		users = self._getUsers()
		self.assertFalse("foobar" in users)


	def test_invalid_input(self):
		"""check all combinations of invalid input"""
		url = self.url + "user_manager"
		self.register_auth(url)
		self.cmd.go(url + "?store=foobar")


	def _add_user(self, username, pw, pw2):
		self.cmd.go(self.url + "user_manager")
		self.cmd.formvalue("add_user","user",username)
		self.cmd.formvalue("add_user","new_pw",pw)
		self.cmd.formvalue("add_user","new_pw2",pw2)
		self.cmd.submit()


	def _del_user(self, username):
		self.cmd.go(self.url + "user_manager")
		self.cmd.formvalue("del_user","user",username)
		self.cmd.submit()


	def _change_password(self, username, pw, pw2):
		self.cmd.go(self.url + "user_manager")
		self.cmd.formvalue("change_password","user",username)
		self.cmd.formvalue("change_password","new_pw",pw)
		self.cmd.formvalue("change_password","new_pw2",pw2)
		self.cmd.submit()


	def _getUsers(self):
		url = self.url + "user_manager"
		self.register_auth(url)
		self.cmd.go(url)
		self.cmd.find("Data.Status.Plugins.user_manager=([\w:]+)")
		return self.locals["__match__"].split(":")

