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

import cryptobox.plugins.base
import cryptobox.plugins.manage
from cryptobox.core.exceptions import *


class volume_props(cryptobox.plugins.base.CryptoBoxPlugin):

	plugin_capabilities = [ "volume" ]
	plugin_visibility = [ "volume" ]
	request_auth = False
	rank = 30


	def do_action(self, **args):
		import os
		## include all plugins marked as "properties"
		## skip ourselves to prevent recursion
		self.props_plugins = [e for e in cryptobox.plugins.manage.PluginManager(self.cbox,
				self.cbox.prefs["Locations"]["PluginDir"]).get_plugins()
				if ("properties") in (e.get_visibility()) \
						and (e.get_name() != self.get_name())]
		## sort plugins by rank
		self.props_plugins.sort(cmp = self.__cmp_plugins_rank)
		## set the name of the templates for every plugin
		load_string = ""
		for p in self.props_plugins:
			## skip all volume plugins that are not suitable
			## (e.g. chpasswd for plain containers)
			if not p.is_useful(self.device):
				continue
			p.device = self.device
			plfname = os.path.join(p.plugin_dir, str(p.do_action(**args)) + ".cs")
			load_string += "<?cs include:'%s' ?>" %  plfname
		## this is a little bit ugly: as it is not possible, to load cs files via
		## 'linclude' (see clearsilver doc) if they use previously defined macros
		## (see clearsilver mailing list thread
		## 'linclude file which calls a macro' - 27th December 02005)
		## our workaround: define the appropriate "include" (not 'linclude')
		## command as a hdf variable - then we can include it via 'evar'
		self.hdf[self.hdf_prefix + 'includePlugins'] = load_string
		return "volume_properties"
	

	def get_status(self):
		return ":".join([ e.get_name() for e in self.props_plugins ])
	

	def load_dataset(self, hdf):
		"""Override the parent's function

		we have to get the data from all included plugins
		"""
		for plugin in self.props_plugins:
			## retrieve the results of an included plugin
			plugin.load_dataset(hdf)
		## call our parent's method
		cryptobox.plugins.base.CryptoBoxPlugin.load_dataset(self, hdf)


	def __cmp_plugins_rank(self, p1, p2):
		order = p1.get_rank() - p2.get_rank()
		if order < 0:
			return -1
		elif order == 0:
			return 0
		else:
			return 1

