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
import twill

class unittests(WebInterfaceTestClass):

	
	def test_read_form(self):
		"""Simply check if the plugin works
		"""
		## umount, if necessary
		cbox_tools.umount(self.device)
		url = self.url + "volume_mount?weblang=en&device=" + self.device_html
		self.register_auth(url)
		self.cmd.go(url)
		self.cmd.find('Open this volume')
		self.cmd.find('Data.Status.Plugins.volume_mount=passive')
	

	def test_mount(self):
		"""Do all variations of mount/umount actions.
		"""
		url = self.url + "volume_mount?weblang=en&device=" + self.device_html
		self.register_auth(url)
		## umount, if necessary
		cbox_tools.umount(self.device)
		## we may not split these tests into two functions, as the order
		## is important (we must leave a clean plain volume behind)
		self.__do_tests_with_luks()
		self.__do_tests_with_plain()
	

	def __do_tests_with_luks(self):
		"""Some tests with a luks partition.
		"""
		url = self.url + "volume_mount?weblang=en&device=" + self.device_html
		self.__format_luks()
		## mount the volume
		self.cmd.go(url)
		self.cmd.find('Open this volume')
		# the following _should_ work, but it does not - probably a parsing problem
		# of twill - for now we use the direct link instead
		#self.cmd.formvalue("mount", "pw", "foo")
		#self.cmd.submit()
		self.cmd.go(url + "&action=mount_luks&pw=foo")
		self.cmd.find('Volume opened')
		self.cmd.find('Data.Status.Plugins.volume_mount=active')
		## try to mount active volume
		self.cmd.go(url + "&action=mount_luks&pw=foo")
		self.cmd.find('The volume is already open.')
		## close the volume
		# the following _should_ work, but it does not - probably a parsing problem
		# of twill - for now we use the direct link instead
		#self.cmd.submit()
		self.cmd.go(url + "&action=umount")
		self.cmd.find('Volume closed')
		self.cmd.find('Data.Status.Plugins.volume_mount=passive')
		## try plain instead of luks
		self.cmd.go(url + "&action=mount_plain")
		self.cmd.find('Data.Status.Plugins.volume_mount=passive')
		self.cmd.find('Unknown format')
		## no password supplied
		self.cmd.go(url + "&action=mount_luks")
		self.cmd.find('Data.Status.Plugins.volume_mount=passive')
		self.cmd.find('Missing password')
		## wrong password supplied
		self.cmd.go(url + "&action=mount_luks&pw=bar")
		self.cmd.find('Data.Status.Plugins.volume_mount=passive')
		self.cmd.find('Maybe you entered a wrong password?')
	

	def __do_tests_with_plain(self):
		"""Some tests with a plain partition.
		"""
		url = self.url + "volume_mount?weblang=en&device=" + self.device_html
		self.__format_plain()
		## open plain volume
		self.cmd.go(url)
		self.cmd.find('Open this volume')
		# the following _should_ work, but it does not - probably a parsing problem
		# of twill - for now we use the direct link instead
		#self.cmd.submit()
		self.cmd.go(url + "&action=mount_plain")
		self.cmd.find('Volume opened')
		self.cmd.find('Data.Status.Plugins.volume_mount=active')
		## try to mount active volume
		self.cmd.go(url + "&action=mount_plain")
		self.cmd.find('The volume is already open.')
		## umount
		# the following _should_ work, but it does not - probably a parsing problem
		# of twill - for now we use the direct link instead
		#self.cmd.submit()
		self.cmd.go(url + "&action=umount")
		self.cmd.find('Volume closed')
		self.cmd.find('Data.Status.Plugins.volume_mount=passive')
		## try to umount closed volume
		self.cmd.go(url + "&action=umount")
		self.cmd.find('The volume is already closed.')


	def __format_luks(self):
		"""Format a luks partition.
		"""
		url = self.url + "volume_format_fs?weblang=en&device=" + self.device_html
		self.register_auth(url)
		self.cmd.go(url)
		self.cmd.find('select name="fs_type"')
		# the following _should_ work, but it does not - probably a parsing problem
		# of twill - for now we use the direct link instead
		#self.cmd.formvalue("set_type", "fs_type", "linux")
		#self.cmd.formvalue("set_type", "container_type", "luks")
		#self.cmd.formvalue("set_type", "confirm", "1")
		#self.cmd.submit()
		self.cmd.go(url + "&fs_type=linux&container_type=luks&confirm=1&store=step1")
		self.cmd.find('name="crypto_password"')
		# the following _should_ work, but it does not - probably a parsing problem
		# of twill - for now we use the direct link instead
		#self.cmd.formvalue("set_luks", "crypto_password", "foo")
		#self.cmd.formvalue("set_luks", "crypto_password2", "foo")
		#self.cmd.submit()
		self.cmd.go(url + "&store=step2&container_type=luks&fs_type=windows&" \
				+ "crypto_password=foo&crypto_password2=foo")
		self.cmd.find('Formatting is running')
		self.__wait_until_ready()
	

	def __format_plain(self):
		"""Format a plaintext partition.
		"""
		url = self.url + "volume_format_fs?weblang=en&device=" + self.device_html
		self.register_auth(url)
		self.cmd.go(url)
		self.cmd.find('select name="fs_type"')
		# the following _should_ work, but it does not - probably a parsing problem
		# of twill - for now we use the direct link instead
		#self.cmd.formvalue("set_type", "fs_type", "windows")
		#self.cmd.formvalue("set_type", "container_type", "plain")
		#self.cmd.formvalue("set_type", "confirm", "1")
		#self.cmd.submit()
		self.cmd.go(url + "&store=step1&confirm=1&container_type=plain&fs_type=windows")
		self.cmd.find('Formatting is running')
		self.__wait_until_ready()
	

	def __wait_until_ready(self):
		"""Wait until the device is ready again.
		"""
		import time
		finish_time = time.time() + 120
		while self.__is_device_busy():
			if (time.time() > finish_time):
				self.fail("timeout for plain formatting expired")
			time.sleep(5)
			
	
	def __is_device_busy(self):
		"""Check if the device is busy.
		"""
		url = self.url + "volume_format_fs?weblang=en&device=" + self.device_html
		self.register_auth(url)
		self.cmd.go(url)
		try:
			self.cmd.find("Disk is busy")
			return True
		except twill.errors.TwillAssertionError:
			return False

