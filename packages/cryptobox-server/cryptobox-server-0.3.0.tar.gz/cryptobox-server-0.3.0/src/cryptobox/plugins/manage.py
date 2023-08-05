# $Id: manage.py 666 2007-01-08 02:21:16Z lars $
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

"""Manages the pluggable features of the CryptoBox.
"""

__revision__ = "$Id"

import os


class PluginManager:
	"""manage available plugins"""

	def __init__(self, cbox, plugin_dirs=".", site_class=None):
		self.cbox = cbox
		self.site = site_class
		if hasattr(plugin_dirs, "__iter__"):
			self.plugin_dirs = [os.path.abspath(d) for d in plugin_dirs]
		else:
			self.plugin_dirs = [os.path.abspath(plugin_dirs)]
		self.plugin_list = self.__get_all_plugins()

	
	def get_plugins(self):
		"""Return a list of all feature instances.
		"""
		return self.plugin_list[:]
	

	def get_plugin(self, name):
		"""Return the specified feature as an instance.
		"""
		for plugin in self.plugin_list[:]:
			if plugin.get_name() == name:
				return plugin
		return None


	def __get_all_plugins(self):
		"""Return all available features as instances.
		"""
		plist = []
		for plfile in self.__get_plugin_files():
			plist.append(self.__get_plugin_class(plfile))
		return plist


	def __get_plugin_class(self, plfile):
		"""Return a instance object of the give feature.
		"""
		import imp
		name = os.path.basename(plfile)[:-3]
		try:
			pl_class = getattr(imp.load_source(name, plfile), name)
		except AttributeError:
			return None
		return pl_class(self.cbox, os.path.dirname(plfile), self.site)
	

	def __get_plugin_files(self):
		"""Retrieve all python files that may potentially be a feature.
		"""
		result = []
		if self.cbox and self.cbox.prefs["Main"]["DisabledPlugins"]:
			disabled = self.cbox.prefs["Main"]["DisabledPlugins"]
		else:
			disabled = []
		for pdir in [os.path.abspath(e) for e in self.plugin_dirs
				if os.access(e, os.R_OK) and os.path.isdir(e)]:
			for plname in [f for f in os.listdir(pdir)]:
				if plname in disabled:
					if self.cbox:
						self.cbox.log.info(
								"Skipping plugin '%s' (disabled via config)" % plname)
					continue
				pldir = os.path.join(pdir, plname)
				plfile = os.path.join(pldir, plname + ".py")
				if os.path.isfile(plfile) and os.access(plfile, os.R_OK):
					result.append(plfile)
		return result


if __name__ == "__main__":
	MANAGER = PluginManager(None, "../plugins")
	for one_plugin in MANAGER.get_plugins():
		if not one_plugin is None:
			print "Plugin: %s" % one_plugin.get_name()

