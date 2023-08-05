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
		"""Simply check if the plugin works.
		"""
		url = self.url + "volume_format_fs?weblang=en&device=" + self.device_html
		self.register_auth(url)
		self.cmd.go(url)
		self.cmd.find('Initializing filesystem')


	def test_invalid_actions(self):
		"""Try to issue some invalid orders.
		"""
		url = self.url + "volume_format_fs?weblang=en&device=" + self.device_html
		self.register_auth(url)
		## make sure, it is not mounted
		cbox_tools.umount(self.device)
		## try invalid filesystem type
		self.cmd.go(url + "&fs_type=foo")
		self.cmd.find('Initializing filesystem')
		## try invalid container type
		self.cmd.go(url + "&container_type=foo")
		self.cmd.find('Initializing filesystem')
		## missing confirmation
		self.cmd.go(url + "&store=step1")
		self.cmd.find('Confirmation missing')
		## call luks form
		self.cmd.go(url + "&store=step1&confirm=1&container_type=luks")
		self.cmd.find('name="crypto_password2"')
		## try 'step2' with plain container type
		self.cmd.go(url + "&store=step2&confirm=1&container_type=plain")
		self.cmd.find('Initializing filesystem')
		## try invalid 'store'
		self.cmd.go(url + "&store=foo")
		self.cmd.find('Initializing filesystem')
		## try without password
		self.cmd.go(url + "&store=step2&container_type=luks&fs_type=windows" \
				+ "&crypto_password=&crypto_password2=foo")
		self.cmd.find('Missing password')
		## try with different passwords
		self.cmd.go(url + "&store=step2&container_type=luks&fs_type=windows" \
				+ "&crypto_password=bar&crypto_password2=foo")
		self.cmd.find('Different passwords')
	

	def test_format_open_device(self):
		"""Try to format an open device.
		"""
		url_format = self.url + "volume_format_fs?weblang=en&device=" \
				+ self.device_html
		self.register_auth(url_format)
		url_mount = self.url + "volume_mount?weblang=en&device=" \
				+ self.device_html
		self.register_auth(url_mount)
		## mount device - do not care, if it was mounted before
		self.cmd.go(url_mount + "&action=mount_plain")
		self.cmd.find('Data.Status.Plugins.volume_mount=active')
		## try plain device
		self.cmd.go(url_format + "&store=step1&confirm=1&container_type=plain&" \
				+ "fs_type=linux")
		self.cmd.find('This action is not available while the volume is active.')
		## try luks device
		self.cmd.go(url_format + "&store=step2&container_type=luks&fs_type=" \
				+ "windows&crypto_password=foo&crypto_password2=foo")
		self.cmd.find('This action is not available while the volume is active.')
		## umount
		cbox_tools.umount(self.device)
	

	def test_format_device(self):
		"""Formatting of a device was done in 'volume_mount' plugin tests.
		"""
		pass

