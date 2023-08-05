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

COMMON_STRING = 'Volume plugins'

class unittests(WebInterfaceTestClass):

	def test_read_form(self):
		"""Check if the 'plugin_manager' works.
		"""
		url = self.url + "plugin_manager?weblang=en"
		self.register_auth(url)
		self.cmd.go(url)
		self.cmd.find(COMMON_STRING)


	def test_set_options(self):
		"""Do some various stuff.
		"""
		#TODO: these 'tests' are really a bit stupid - someone should fix this
		url = self.url + "plugin_manager"
		self.register_auth(url)
		self.cmd.go(url + r"?plugin_name=t/-!")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?plugin_name=foobar")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?plugin_name=disks&action=up")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?plugin_name=disks&action=down")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?store=1&dis/ks_listed")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?store=1&disks_listed&disks_visible_menu")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?store=1&disks_listed&disks_visible_menu=1&disks_rank=50")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?store=1&disks_listed&disks_visible_menu=1&disks_rank=x")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?store=1&disks_listed&disks_visible_menu=1&disks_auth=1")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?store=1&disks_listed&disks_visible_menu=1&disks_rank=50&disks_auth=1")
		self.cmd.find(COMMON_STRING)
		
		
	def test_move_up(self):
		"""Move some plugins up.
		"""
		#TODO: if we want to be perfect, then we should check the change of the rank
		url = self.url + "plugin_manager"
		self.register_auth(url)
		self.cmd.go(url + r"?plugin_name=disks&action=up")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?store=1&disks_listed&disks_visible_menu=1&disks_rank=0")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?plugin_name=disks&action=up")
		self.cmd.find(COMMON_STRING)


	def test_move_down(self):
		"""Move some plugins down.
		"""
		## TODO: if we want to be perfect, then we should check the change of the rank
		url = self.url + "plugin_manager"
		self.register_auth(url)
		self.cmd.go(url + r"?plugin_name=disks&action=down")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?store=1&disks_listed&disks_visible_menu=1&disks_rank=100")
		self.cmd.find(COMMON_STRING)
		self.cmd.go(url + r"?plugin_name=disks&action=down")
		self.cmd.find(COMMON_STRING)

