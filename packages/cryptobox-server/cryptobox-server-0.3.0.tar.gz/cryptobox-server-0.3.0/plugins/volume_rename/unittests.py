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
import cryptobox.tests.tools as cbox_tools

class unittests(WebInterfaceTestClass):

	def test_read_form(self):
		"""Check if the 'volume_rename' plugin works.
		"""
		url = self.url + "volume_rename?weblang=en&device=" + self.device_html
		self.register_auth(url)
		## umount, if necessary
		cbox_tools.umount(self.device)
		## check a language string
		self.cmd.go(url)
		self.cmd.find('Change name')


	def test_rename(self):
		"""Try to rename the volume.
		"""
		## umount, if necessary
		cbox_tools.umount(self.device)
		save_name = self.__get_name()
		## rename if the name is already "foo"
		if save_name == "foo":
			self.__set_name("bar")
		## set 'foo'
		self.__set_name("foo")
		self.cmd.find('The name of this volume was changed successfully.')
		self.assertEquals("foo", self.__get_name())
		## set 'bar'
		self.__set_name("bar")
		self.cmd.find('The name of this volume was changed successfully.')
		self.assertEquals("bar", self.__get_name())
		## set the same name twice to catch all lines of code
		self.__set_name("bar")
		self.cmd.notfind('The name of this volume was changed successfully.')
		self.assertEquals("bar", self.__get_name())
		self.__set_name(save_name)
		self.assertEquals(save_name, self.__get_name())
	

	def test_invalid_names(self):
		"""Setting of invalid names should fail.
		"""
		## umount, if necessary
		cbox_tools.umount(self.device)
		save_name = self.__get_name()
		## we want to avoid, that if the previous name is (by accident) 'foo'
		## then the later search for "changed successfully" would fail
		if save_name == "foo":
			self.__set_name("bar")
		self.__set_name("foo")
		self.cmd.find('The name of this volume was changed successfully.')
		self.assertEquals("foo", self.__get_name())
		self.__set_name("foo:")
		self.cmd.find("Changing of volume's name failed")
		self.assertEquals("foo", self.__get_name())
		self.__set_name("foo/")
		self.cmd.find("Changing of volume's name failed")
		self.assertEquals("foo", self.__get_name())
		self.__set_name("foo/")
		self.cmd.find("Changing of volume's name failed")
		self.assertEquals("foo", self.__get_name())
		self.__set_name("foo*")
		self.cmd.find("Changing of volume's name failed")
		self.assertEquals("foo", self.__get_name())
		self.__set_name("foo(")
		self.cmd.find("Changing of volume's name failed")
		self.assertEquals("foo", self.__get_name())
		self.__set_name("")
		self.cmd.notfind("Changing of volume's name failed")
		self.assertEquals("foo", self.__get_name())
		self.__set_name(save_name)
		self.assertEquals(save_name, self.__get_name())


	def test_rename_while_open(self):
		"""Try to change the name of the volume while it is open.
		"""
		## umount, if necessary
		cbox_tools.umount(self.device)
		save_name = self.__get_name()
		## first set the name to 'bar'
		self.__set_name("bar")
		mount_url = self.url + "volume_mount?weblang=en&device=" + self.device_html
		self.register_auth(mount_url)
		name_url = self.url + "volume_rename?weblang=en&device=" + self.device_html
		self.register_auth(name_url)
		self.cmd.go(mount_url + "&action=mount_plain")
		self.cmd.find('Volume opened')
		## we have to do it manually, as there is no form when it is open
		self.cmd.go(name_url + "&store=1&vol_name=foo")
		self.cmd.find('You may not rename a volume while it is open.')
		self.assertEquals("bar", self.__get_name())
		self.cmd.go(mount_url + "&action=umount")
		self.__set_name(save_name)
		self.assertEquals(save_name, self.__get_name())


	def test_name_in_use(self):
		"""Try to set a name that is already in use.
		"""
		## umount, if necessary
		cbox_tools.umount(self.device)
		used_name = [ e.get_name() for e in self.cbox.get_container_list()
				if e.get_device() != self.device ]
		if not used_name:
			self.fail("could not find another device for this test")
		old_name = self.__get_name()
		self.assertNotEquals(old_name, used_name[0])
		self.__set_name(used_name[0])
		self.cmd.find('The new name is already in use by another volume.')
		self.assertEquals(old_name, self.__get_name())


	def __set_name(self, name):
		"""Set the name of a volume.
		"""
		name = name.replace(" ", "%20")
		url = self.url + "volume_rename?weblang=en&device=" + self.device_html
		self.register_auth(url)
		# the following should work, but twill seems to have problems to recognize
		# the form - fix this later
		#self.cmd.go(url)
		#self.cmd.formvalue("set_name", "vol_name", name)
		#self.cmd.submit()
		self.cmd.go(url + "&vol_name=%s&store=1" % name)
	

	def __get_name(self):
		"""Retrieve the current name of the volume.
		"""
		url = self.url + "volume_rename?weblang=en&device=" + self.device_html
		self.register_auth(url)
		self.cmd.go(url)
		self.cmd.find("Data.Status.Plugins.volume_rename=(.*)$", "m")
		return self.locals["__match__"]
	
