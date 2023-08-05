#!/usr/bin/env python
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

"""Unittests for cryptobox.core.tools
"""

__revision__ = "$Id"


import cryptobox.core.tools as cbx_tools
from cryptobox.tests.base import CommonTestClass
import os


class CryptoBoxToolsTests(CommonTestClass):
	"""All unittests for cryptoboxtools
	"""

	def test_get_absolute_devicename(self):
		"""check the get_absolute_devicename function
		"""
		func = cbx_tools.get_absolute_devicename
		self.assertTrue(func(os.path.basename(self.device)) == self.device)
		self.assertTrue(func("loop0") == "/dev/loop0")
		self.assertTrue(func(os.path.devnull) == os.path.devnull)


	def test_find_major_minor_of_device(self):
		"""check the find_major_minor_of_device function
		"""
		func = cbx_tools.find_major_minor_of_device
		self.assertTrue(func(os.path.devnull) == (1, 3))
		self.assertTrue(func("/dev/nothere") is None)


	def test_find_major_minor_device(self):
		"""check the find_major_minor_device function
		"""
		func = cbx_tools.find_major_minor_device
		path = os.path.join(os.path.sep, "dev")
		self.assertTrue(os.path.devnull in func(path, 1, 3))
		self.assertFalse(os.path.devnull in func(path, 2, 3))
		self.assertFalse(None in func(path, 17, 23))


	def test_is_part_of_blockdevice(self):
		"""check the is_part_of_blockdevice function
		"""
		func = cbx_tools.is_part_of_blockdevice
		self.assertTrue(func(self.blockdevice, self.device))
		self.assertFalse(func(self.blockdevice, self.blockdevice))
		self.assertFalse(func(self.device, self.blockdevice))
		self.assertFalse(func(self.device, self.device))
		self.assertFalse(func(self.blockdevice, "/dev/hde1"))
		self.assertFalse(func(None, self.blockdevice))
		self.assertFalse(func(self.blockdevice, None))
		self.assertFalse(func(None, ""))
		self.assertFalse(func("loop0", "loop1"))

