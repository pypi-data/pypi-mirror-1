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

class unittests(WebInterfaceTestClass):

	def test_read_logs(self):
		"""Read the log files.
		"""
		log_url = self.url + "logs"
		self.register_auth(log_url)
		self.cmd.go(log_url)
		self.cmd.find('<table class="log">')

	def test_write_logs(self):
		"""Send a log message and read it again.
		"""
		log_text = "unittest - just a marker - please ignore"
		self.cbox.log.error(log_text)
		log_url = self.url + "logs"
		self.register_auth(log_url)
		self.cmd.go(log_url + "?level=ERROR")
		self.cmd.find(log_text)

	def test_invalid_args(self):
		"""Send various invalid input combinations to the 'log' plugin.
		"""
		log_url = self.url + "logs"
		self.cmd.go(log_url + "?lines=10")
		self.cmd.find('<table class="log">')
		self.cmd.go(log_url + "?lines=0")
		self.cmd.find('<table class="log">')
		self.cmd.go(log_url + "?lines=x")
		self.cmd.find('<table class="log">')
		self.cmd.go(log_url + "?size=1000")
		self.cmd.find('<table class="log">')
		self.cmd.go(log_url + "?size=0")
		self.cmd.find('<table class="log">')
		self.cmd.go(log_url + "?size=x")
		self.cmd.find('<table class="log">')
		self.cmd.go(log_url + "?level=foobar")
		self.cmd.find('<table class="log">')
		self.cmd.go(log_url + r"?level=kfj!^(]")
		self.cmd.find('<table class="log">')
		
