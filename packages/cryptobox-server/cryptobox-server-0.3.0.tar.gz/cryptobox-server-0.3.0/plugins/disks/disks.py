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

"""The disks feature of the CryptoBox.
"""

__revision__ = "$Id"

import cryptobox.plugins.base

class disks(cryptobox.plugins.base.CryptoBoxPlugin):
	"""The disk feature of the CryptoBox.
	"""

	plugin_capabilities = [ "system" ]
	plugin_visibility = [ "menu" ]
	request_auth = False
	rank = 10

	def do_action(self):
		"""The action handler.
		"""
		self.cbox.reread_container_list()
		return "disks"


	def get_status(self):
		"""Retrieve the current status of the feature.
		"""
		return ":".join([e.get_device() for e in self.cbox.get_container_list()])

