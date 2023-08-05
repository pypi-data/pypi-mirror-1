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


class plugin_manager(cryptobox.plugins.base.CryptoBoxPlugin):

	plugin_capabilities = [ "system" ]
	plugin_visibility = [ "preferences" ]
	request_auth = True
	rank = 90

	def do_action(self, store=None, action=None, plugin_name=None, **args):
		import re
		if plugin_name:
			## check for invalid characters
			if re.search(r'\W', plugin_name): return "plugin_list"
			plugin_manager = cryptobox.plugins.manage.PluginManager(
					self.cbox, self.cbox.prefs["Locations"]["PluginDir"])
			plugin = plugin_manager.get_plugin(plugin_name)
			if not plugin: return "plugin_list"
			## take only plugins, that are of the same type as the choosen one
			self.plugins = [e for e in plugin_manager.get_plugins()
					if e.plugin_capabilities == plugin.plugin_capabilities and \
					e != "volume_props" ]
			if action == "up":
				self.__move_up(plugin)
			elif action == "down":
				self.__move_down(plugin)
			return "plugin_list"
		elif store:
			for key in args.keys():
				if key.endswith("_listed"):
					if not re.search(r'\W',key):
						self.__set_config(key[:-7], args)
					else:
						self.cbox.log.info("plugin_manager: invalid plugin name (%s)" % \
								str(key[:-7]))
			try:
				self.cbox.prefs.plugin_conf.write()
				self.cbox.log.info("Successfully stored plugin configuration")
			except IOError, err_msg:
				self.cbox.log.warn("Failed to write plugin configuration: %s" % err_msg)
		return "plugin_list"


	def get_status(self):
		plugin_manager = cryptobox.plugins.manage.PluginManager(
				self.cbox, self.cbox.prefs["Locations"]["PluginDir"])
		return ":".join([e.get_name() for e in plugin_manager.get_plugins()])


	def __sort_plugins(self):
		"""sort all plugins in the list according to their rank"""
		def cmp_func(x,y):
			x_rank = x.get_rank()
			y_rank = y.get_rank()
			if x_rank < y_rank:
				return -1
			elif x_rank == y_rank:
				return 0
			else:
				return 1
		self.plugins.sort(cmp = cmp_func)
	
	
	def __distribute_ranks(self):
		"""evenly distribute the 'rank' values according to the current order of
		the list"""
		dist = 100 / (len(self.plugins) - 1)
		for (index, pl) in enumerate(self.plugins):
			pl.set_rank(dist*index)
		try:
			self.cbox.prefs.plugin_conf.write()
		except IOError:
			self.cbox.log.warn("failed to write plugin configuration")


	def __move_up(self, plugin):
		self.__sort_plugins()
		try:
			index = self.plugins.index(plugin)
			## first elements may not move up
			if index == 0:
				return
		except ValueError:
			return
		self.plugins.remove(plugin)
		self.plugins.insert(index-1, plugin)
		self.__distribute_ranks()
		

	def __move_down(self, plugin):
		self.__sort_plugins()
		try:
			index = self.plugins.index(plugin)
			## last elements may not move down
			if index == len(self.plugins) - 1:
				return
		except ValueError:
			return
		self.plugins.remove(plugin)
		self.plugins.insert(index+1, plugin)
		self.__distribute_ranks()


	def __set_config(self, name, args):
		import re
		if not self.cbox.prefs.plugin_conf.has_key(name):
			self.cbox.prefs.plugin_conf[name] = {}
		setting = self.cbox.prefs.plugin_conf[name]
		setting["visibility"] = []
		## look for "_visible_" values and apply them
		pattern = re.compile(r'%s_visible_([\w]+)$' % name)
		for key in args.keys():
			if key.startswith(name + "_visible_"):
				(vis_type, ) = pattern.match(key).groups()
				if vis_type:
					setting["visibility"].append(vis_type)
		## the plugin_manager _must_ always be visible
		if (self.get_name() == name) and (not setting["visibility"]):
			## reset to default
			setting["visibility"] = self.plugin_visibility[:]
		if args.has_key("%s_auth" % name):
			setting["requestAuth"] = True
		else:
			setting["requestAuth"] = False

