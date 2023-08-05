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
from network import CHANGE_IP_DELAY


class unittests(WebInterfaceTestClass):

	def test_ip_change(self):
		'''Change network address.'''
		## the time module is necessary for the CHANGE_IP_DELAY
		import time
		self.register_auth(self.url + "network")
		## do not follow redirects - they would break the test otherwise
		self.cmd.config("acknowledge_equiv_refresh", 0)
		self.cmd.go(self.url + "network")
		## extract the current IP from the network plugin output
		def get_current_ip():
			self.register_auth(self.url + "network")
			self.cmd.go(self.url + "network")
			self.cmd.find(r'Data.Status.Plugins.network=([0-9\.]*)$', "m")
			return self.locals["__match__"]
		orig_ip_text = get_current_ip()
		orig_ip_octs = orig_ip_text.split(".")
		## check, if the original IP is valid (contains four octets)
		self.assertEquals(4, len(orig_ip_octs))
		def set_ip((ip1, ip2, ip3, ip4)):
			self.cmd.go(self.url + "network")
			self.cmd.formvalue("network_address", "ip1", str(ip1))
			self.cmd.formvalue("network_address", "ip2", str(ip2))
			self.cmd.formvalue("network_address", "ip3", str(ip3))
			self.cmd.formvalue("network_address", "ip4", str(ip4))
			self.cmd.submit()
			## sleep a little bit longer than the delay necessary for ip-change
			time.sleep(CHANGE_IP_DELAY + 3)
		set_ip([1,-2,0,1])
		self.assertEquals(orig_ip_text, get_current_ip())
		set_ip([1,0,0,256])
		self.assertEquals(orig_ip_text, get_current_ip())
		set_ip([1,"foo",0,1])
		self.assertEquals(orig_ip_text, get_current_ip())
		new_ip = orig_ip_octs[:]
		new_ip[3] = str((int(orig_ip_octs[3]) + 128) % 256)
		set_ip(new_ip)
		self.assertEquals(".".join(new_ip), get_current_ip())
		set_ip(orig_ip_octs)
		self.assertEquals(orig_ip_text, get_current_ip())


	def test_inputs(self):
		"""Check various input patterns for 'network' plugin.
		"""
		self.register_auth(self.url + "network")
		self.cmd.go(self.url + "network" + "?redirected=1")
		self.cmd.notfind("problem")
		self.cmd.go(self.url + "network" + "?store=set_ip")
		self.cmd.find("server address is not valid")

