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

"""
this module contains all super classes for different tests

just inherit one of its classes and add some test functions

All testclasses based on the classes of this module may assume the following:
	- there is one valid parent blockdevice (self.blockdevice)
	- the blockdevice contains exactly two partitions:
		- part1: vfat, 50MB, formatted (devicename: self.device)
		- part2: ext3, 50MB, formatted
	- self.blockdevice_html and self.device_html are url-escaped strings
	- all databases (pluginconf, volume names, users) are empty

Additional hints:
	- if the current state of self.device is important, then you should umount
	  it before any of these tests: cryptobox.tests.tools.umount(self.device)
"""

__revision__ = "$Id"

import unittest
import twill
import cherrypy 
import cryptobox.web.sites
import cryptobox.tests.base



## commands api: http://twill.idyll.org/commands.html
CBXHOST = "localhost"
CBXPORT = 8081
CBX_URL = "http://%s:%d/" % (CBXHOST, CBXPORT)
LOG_FILE = "/tmp/cryptobox-twill.log"
WEBLOG_FILE = "/tmp/cryptobox-cherrypy.log"
CONF_FILE = 'cryptobox-unittests.conf'


class CommonTestClass(unittest.TestCase):
	"""Super class of all tests of the CryptoBox

	prepare environment, set some values ...
	"""

	def __init__(self, methodName='runTest'):
		unittest.TestCase.__init__(self, methodName)
		import cryptobox.core.settings as cbox_settings
		import cryptobox.tests.tools as testtools
		import os
		## search for a usable block device
		## use /dev/ubd? if possible - otherwise /dev/hd?
		## so it will be possible to use these tests inside of a uml
		self.blockdevice = testtools.find_test_device()
		## umount the partitions of this device (just to be sure)
		for num in range(12):
			testtools.umount("%s%d" % (self.blockdevice, num))
		## format device and partition block device if necessary
		testtools.prepare_partition(self.blockdevice)
		self.blockdevice = testtools.find_test_device()
		self.device = self.blockdevice + "1"
		self.blockdevice_html = self.blockdevice.replace("/", "%2F")
		self.device_html = self.device.replace("/", "%2F")
		
		## remove configuration files
		## first: retrieve the settings directory
		settings_dir = cbox_settings.CryptoBoxSettings(CONF_FILE)\
				["Locations"]["SettingsDir"]
		for filename in [
				cbox_settings.VOLUMESDB_FILE,
				cbox_settings.PLUGINCONF_FILE,
				cbox_settings.USERDB_FILE]:
			try:
				os.unlink(os.path.join(settings_dir, filename))
			except OSError:
				pass



class WebInterfaceTestClass(CommonTestClass):
	'''this class checks the webserver, using "twill"

	the tests in this class are from the browsers point of view, so not
	really unittests.
	fetch twill from: http://twill.idyll.org
	'''

	def __init__(self, methodName='runTest'):
		CommonTestClass.__init__(self, methodName)


	def setUp(self):
		'''configures the cherrypy server that it works nice with twill
		'''
		CommonTestClass.setUp(self)
		cherrypy.config.update({ 
					'server.logToScreen' : False,
					'autoreload.on': False,
					'server.threadPool': 1,
					'server.environment': 'development',
					'server.log_tracebacks': True,
					'server.log_file': WEBLOG_FILE,
					})
		cherrypy.root = cryptobox.web.sites.WebInterfaceSites(CONF_FILE)

		cherrypy.server.start(initOnly=True, serverClass=None)

		from cherrypy._cpwsgi import wsgiApp 
		twill.add_wsgi_intercept(CBXHOST, CBXPORT, lambda: wsgiApp) 

		# grab the output of twill commands
		self.output = open(LOG_FILE,"a")
		twill.set_output(self.output)
		self.cmd = twill.commands
		self.url = CBX_URL
		self.cbox = cherrypy.root.cbox
		self.globals, self.locals = twill.namespaces.get_twill_glocals()


	def tearDown(self):
		'''clean up the room when leaving'''
		## remove intercept.
		twill.remove_wsgi_intercept(CBXHOST, CBXPORT)
		## stop the cryptobox
		cherrypy.root.cleanup()
		## shut down the cherrypy server.
		cherrypy.server.stop()
		self.output.close()
		## inform the parent
		CommonTestClass.tearDown(self)



	def __get_soup():
		browser = twill.commands.get_browser()
		soup = BeautifulSoup(browser.get_html())
		return soup
	

	def register_auth(self, url, user="admin", password="admin"):
		self.cmd.add_auth("CryptoBox", url, user, password)

