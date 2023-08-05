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

"""Some unittests for the core CryptoBox modules.
"""

__revision__ = "$Id"


import cryptobox.core.main
from cryptobox.core.exceptions import *
import cryptobox.core.settings
from cryptobox.tests.base import CommonTestClass
import os


class CryptoBoxDeviceTests(CommonTestClass):
	"""Some unittests for the CryptoBox
	"""

	cb = cryptobox.core.main.CryptoBox()


	def test_allowed_devices(self):
		'''is_device_allowed should accept permitted devices'''
		self.assertTrue(self.cb.is_device_allowed("/dev/loop1"))
		self.assertTrue(self.cb.is_device_allowed("/dev/usb/../loop1"))


	def test_denied_devices(self):
		'''is_device_allowed should fail with not explicitly allowed devices'''
		self.assertFalse(self.cb.is_device_allowed("/dev/hda"))
		self.assertFalse(self.cb.is_device_allowed("/dev/loopa/../hda"))
		self.assertFalse(self.cb.is_device_allowed("/"))
		## this device does not exist -> no permission check possible
		self.assertFalse(self.cb.is_device_allowed("/dev/loop"))



class CryptoBoxConfigTests(CommonTestClass):
	'''test here if everything with the config turns right'''
	files = {
		"configFileOK"	:  "cbox-test_ok.conf",
		"configFileBroken"	:  "cbox-test_broken.conf",
		"nameDBFile"	: "cryptobox_volumes.db",
		"pluginConf"	: "cryptobox_plugins.conf",
		"userDB"	: "cryptobox_users.db",
		"logFile"	: "cryptobox.log",
		"tmpdir"	: "cryptobox-mnt" }
	tmpdirname = ""
	filenames = {}
	configContentOK = """
[Main]
AllowedDevices  = /dev/loop
DefaultVolumePrefix = "Data "
DefaultCipher   = aes-cbc-essiv:sha256
[Locations]
SettingsDir    = %s
MountParentDir  = %s
TemplateDir		= ../templates
LangDir			= ../lang
DocDir			= ../doc/html
PluginDir		= ../plugins
EventDir			= ../event-scripts
[Log]
Level           = debug
Destination        = file
Details     = %s/cryptobox.log
[WebSettings]
Stylesheet	= /cryptobox-misc/cryptobox.css
[Programs]
blkid			= /sbin/blkid
cryptsetup		= /sbin/cryptsetup
super			= /usr/bin/super
CryptoBoxRootActions	= CryptoBoxRootActions
"""


	def setUp(self):
		'''prepare the test
		'''
		CommonTestClass.setUp(self)
		## generate all files in tmp and remember the names
		import tempfile
		self.tmpdirname = tempfile.mkdtemp(prefix="cbox-")
		for tfile in self.files.keys():
			self.filenames[tfile] = os.path.join(self.tmpdirname, self.files[tfile])
		self.write_config()


	def tearDown(self):
		'''remove the created tmpfiles'''
		# remove temp files
		for tfile in self.filenames.values():
			compl_name = os.path.join(self.tmpdirname, tfile)
			if os.path.exists(compl_name): 
				os.remove(compl_name)
		# remove temp dir
		os.rmdir(self.tmpdirname)
		CommonTestClass.tearDown(self)


	def test_config_init(self):
		'''Check various branches of config file loading'''
		self.assertRaises(CBConfigUnavailableError,
				cryptobox.core.main.CryptoBox,"/invalid/path/to/config/file")
		self.assertRaises(CBConfigUnavailableError,
				cryptobox.core.main.CryptoBox,"/etc/shadow")
		## check one of the following things:
		##  1) are we successfully using an existing config file?
		##  2) do we break, if no config file is there?
		## depending on the existence of a config file, only one of these conditions
		## can be checked - hints for more comprehensive tests are appreciated :)
		for cfile in ['cryptobox.conf']:
			if os.path.exists(cfile):
				cryptobox.core.main.CryptoBox()
				break	# this skips the 'else' clause
		else:
			self.assertRaises(CBConfigUnavailableError,
					cryptobox.core.main.CryptoBox) 
		self.assertRaises(CBConfigUnavailableError,
				cryptobox.core.main.CryptoBox,[])

	
	def test_broken_configs(self):
		"""Check various broken configurations
		"""
		self.write_config("SettingsDir", "SettingsDir=/foo/bar",
				filename=self.filenames["configFileBroken"])
		self.assertRaises(CBConfigError, cryptobox.core.main.CryptoBox,
				self.filenames["configFileBroken"])
		self.write_config("Level", "Level = ho",
				filename=self.filenames["configFileBroken"])
		self.assertRaises(CBConfigError, cryptobox.core.main.CryptoBox,
				self.filenames["configFileBroken"])
		self.write_config("Destination", "Destination = foobar",
				filename=self.filenames["configFileBroken"])
		self.assertRaises(CBConfigError, cryptobox.core.main.CryptoBox,
				self.filenames["configFileBroken"])
		self.write_config("super", "super=/bin/invalid/no",
				filename=self.filenames["configFileBroken"])
		self.assertRaises(CBConfigError, cryptobox.core.main.CryptoBox,
				self.filenames["configFileBroken"])
		self.write_config("CryptoBoxRootActions", "#not here",
				filename=self.filenames["configFileBroken"])
		self.assertRaises(CBConfigError, cryptobox.core.main.CryptoBox,
				self.filenames["configFileBroken"])
		self.write_config("CryptoBoxRootActions", "CryptoBoxRootActions = /bin/false",
				filename=self.filenames["configFileBroken"])
		self.assertRaises(CBEnvironmentError, cryptobox.core.main.CryptoBox,
				self.filenames["configFileBroken"])
	

	def write_config(self, replace=None, newline=None, filename=None):
		"""write a config file and (optional) replace a line in it"""
		import re
		if not filename:
			filename = self.filenames["configFileOK"]
		content = self.configContentOK % \
				(self.tmpdirname, self.tmpdirname, self.tmpdirname)
		if replace:
			pattern = re.compile('^' + replace + '\\s*=.*$', flags=re.M)
			content = re.sub(pattern, newline, content)
		cfile = open(filename, "w")
		cfile.write(content)
		cfile.close()

