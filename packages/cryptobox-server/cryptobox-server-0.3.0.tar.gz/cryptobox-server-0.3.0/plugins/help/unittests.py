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
from twill.errors import *

class unittests(WebInterfaceTestClass):

	def test_help_language_texts(self):
		'''help pages should be available in different languages'''

		## check english help pages
		self.cmd.go(self.url + "help?weblang=en")
		self.cmd.find("Table of Contents")
		self.cmd.find("Getting started")
		(lang,page) = self._getHelpStatus()
		self.assertTrue(lang == "en")
		self.assertTrue(page == "CryptoBoxUser")

		## check german help pages
		self.cmd.go(self.url + "help?weblang=de")
		self.cmd.find("Table of Contents")
		self.cmd.find("Wie geht es los")
		(lang,page) = self._getHelpStatus()
		self.assertTrue(lang == "de")
		self.assertTrue(page == "CryptoBoxUser")

		## check slovene help pages
		self.cmd.go(self.url + "help?weblang=sl")
		self.assertRaises(TwillAssertionError, self.cmd.notfind, "Table of Contents")
		## add a slovene text here, as soon as the help is translated
		(lang,page) = self._getHelpStatus()
		## change this to "sl" as soon as the help is translated
		self.assertTrue(lang == "en")
		self.assertTrue(page == "CryptoBoxUser")

		## check french help pages
		self.cmd.go(self.url + "help?weblang=fr")
		self.assertRaises(TwillAssertionError, self.cmd.notfind, "Table of Contents")
		## add a french text here, as soon as the help is translated
		(lang,page) = self._getHelpStatus()
		## change this to "fr" as soon as the help is translated
		self.assertTrue(lang == "en")
		self.assertTrue(page == "CryptoBoxUser")

		## test a random language - it should fall back to english
		self.cmd.go(self.url + "help?weblang=foobar")
		self.assertRaises(TwillAssertionError, self.cmd.notfind, "Table of Contents")
		(lang,page) = self._getHelpStatus()
		self.assertTrue(lang == "en")
		self.assertTrue(page == "CryptoBoxUser")
	

	def test_help_pages(self):
		"""check invalid page requests"""
		self.cmd.go(self.url + "help?page=foobar")
		(lang,page) = self._getHelpStatus()
		self.assertTrue(page == "CryptoBoxUser")

		self.cmd.go(self.url + "help?page=CryptoBoxUser")
		(lang,page) = self._getHelpStatus()
		self.assertTrue(page == "CryptoBoxUser")


	def test_help_default_languages(self):
		"""check invalid page requests"""
		self.cmd.go(self.url + "help?weblang=foobar")
		(lang,page) = self._getHelpStatus()
		self.assertTrue(lang == "en")


	def _getHelpStatus(self):
		self.cmd.find(r'Data.Status.Plugins.help=(.*)$', "m")
		return tuple(self.locals["__match__"].split(":"))

