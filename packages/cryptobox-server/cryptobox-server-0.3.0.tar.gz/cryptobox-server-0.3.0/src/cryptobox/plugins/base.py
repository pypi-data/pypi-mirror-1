# $Id: base.py 798 2007-02-09 16:47:56Z age $
#
# parent class for all plugins of the CryptoBox
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

"""All features should inherit from this class.
"""

__revision__ = "$Id"

import os
import cherrypy
import imp


class CryptoBoxPlugin:
	"""The base class of all features.
	"""

	## default capability is "system" - the other supported capability is: "volume"
	plugin_capabilities = [ "system" ]

	## where should the plugin be visible by default?
	plugin_visibility = [ "preferences" ]

	## does this plugin require admin authentification?
	request_auth = False

	## default rank (0..100) of the plugin in listings (lower value means higher priority)
	rank = 80


	## default icon of this plugin (relative path)
	default_icon_filename = "plugin_icon"

	## fallback icon file (in the common plugin directory)
	fallback_icon_filename = "plugin_icon_unknown"


	def __init__(self, cbox, plugin_dir, site_class=None):
		if cbox:
			self.cbox = cbox
		else:
			## define empty dummy class as a replacement for a cbox instance
			class CBoxPrefs(dict):
				plugin_conf = {}
			class CBoxLogger:
				def debug(self, text):
					pass
				info = debug
				warn = debug
				error = debug
			class CBoxMinimal:
				prefs = CBoxPrefs()
				prefs["PluginSettings"] = {}
				log = CBoxLogger()
			self.cbox = CBoxMinimal()
		self.hdf = {}
		self.plugin_dir = plugin_dir
		self.hdf_prefix = "Data.Plugins.%s." % self.get_name()
		self.site = site_class
		if not self.get_name() in self.cbox.prefs.plugin_conf:
			## initialize plugin configuration
			self.cbox.prefs.plugin_conf[self.get_name()] = {}
		self.prefs = self.cbox.prefs.plugin_conf[self.get_name()]
		self.cbox.log.debug("Plugin '%s': settings " % self.get_name() + \
				"loaded from plugin configuration file: %s" % str(self.prefs))
		if self.get_name() in self.cbox.prefs["PluginSettings"]:
			self.defaults = self.cbox.prefs["PluginSettings"][self.get_name()]
		else:
			self.defaults = {}
		self.cbox.log.debug("Plugin '%s': configuration " % self.get_name() + \
				"settings imported from global config file: %s" % str(self.defaults))
		## load a possibly existing "root_action.py" scripts as self.root_action
		if os.path.isfile(os.path.join(self.plugin_dir, "root_action.py")):
			self.root_action = imp.load_source("root_action",
					os.path.join(self.plugin_dir, "root_action.py"))
		else:
			self.root_action = None


	def do_action(self, **args):
		"""Override do_action with your plugin code
		"""
		raise Exception, \
				"undefined action handler ('do_action') in plugin '%s'" % self.get_name()
	

	def get_status(self):
		"""you should override this, to supply useful state information
		"""
		raise Exception, \
				"undefined state handler ('get_status') in plugin '%s'" % self.get_name()
	
	def is_useful(self, device):
		"""Return if this plugin is useful for a specific device.

		This should only be used for volume plugins. Nice for output filtering.
		"""
		return True


	def get_name(self):
		"""the name of the python file (module) should be the name of the plugin
		"""
		return self.__module__
	

	def handle_event(self, event_name, event_info=None):
		"""Any plugin that wants to define event actions may override this.

		currently only the following events are defined:
			- "bootup" (the cryptobox server is starting)
			- "shutdown" (the cryptobox server is stopping)
		"""
		pass

	
	def get_warnings(self):
		"""Return a priority and a warning, if the plugin detects a misconfiguration

		valid prioritie ranges are:
			- 80..99	loss of data is possible
			- 60..79	the cryptobox will probably not work at all
			- 40..59	important features will propably not work
			- 20..39	heavy security risk OR broken recommended features
			- 00..19	possible mild security risk OR broken/missing optional features
		"""
		return []


	@cherrypy.expose
	def download(self, **kargs):
		"""Deliver a downloadable file - by default return nothing
		"""
		return ""


	@cherrypy.expose
	def get_icon(self, image=None, **kargs):
		"""return the image data of the icon of the plugin
		
		the parameter 'image' may be used for alternative image locations (relative
		to the directory of the plugin)
		'**kargs' is necessary, as a 'weblang' attribute may be specified (and ignored)
		"""
		import re
		icon_ext = self.__get_default_icon_extension()
		if (image is None) or (not re.match(r'[\w\-\.]*$', image)):
			plugin_icon_file = os.path.join(self.plugin_dir,
					"%s.%s" % (self.default_icon_filename, icon_ext))
		else:
			plugin_icon_file = os.path.join(self.plugin_dir, image)
		## check if we can find the fallback plugin icon in one of the
		## plugin directories
		if not os.access(plugin_icon_file, os.R_OK):
			for ppath in self.cbox.prefs["Locations"]["PluginDir"]:
				plugin_icon_file = os.path.join(ppath,
						"%s.%s" % (self.fallback_icon_filename, icon_ext))
				if plugin_icon_file:
					break
		return cherrypy.lib.cptools.serveFile(plugin_icon_file)
	

	def __get_default_icon_extension(self):
		"""Return 'png' or 'gif' depending on the 'User-Agent' request header

		This is useful, as IE 5.5/6.0 does not render transparent png graphics properly
		Internet Explorer 5.5/6.0: return 'gif'
		everything else: return 'png'
		"""
		if ("User-Agent" in cherrypy.request.headers) and \
				((cherrypy.request.headers["User-Agent"].find("MSIE 5.5;") != -1) or \
				(cherrypy.request.headers["User-Agent"].find("MSIE 6.0;") != -1)):
			return "gif"
		else:
			return "png"


	def get_template_filename(self, template_name):
		"""return the filename of the template, if it is part of this plugin

		use this function to check, if the plugin provides the specified template
		"""
		result_file = os.path.join(self.plugin_dir, template_name + ".cs")
		if os.access(result_file, os.R_OK) and os.path.isfile(result_file):
			return result_file
		else:
			return None


	def get_language_data(self):
		"""Retrieve the language data of the feature.

		Typically this is the content of the language.hdf file as a HDF object.
		"""
		import neo_cgi, neo_util
		lang_hdf = neo_util.HDF()
		lang_file = os.path.join(self.plugin_dir, 'language.hdf')
		try:
			lang_hdf.readFile(lang_file)
		except (neo_util.Error, neo_util.ParseError):
			self.cbox.log.error("failed to load language file (%s) of plugin (%s):" % \
					(lang_file, self.get_name()))
		return lang_hdf


	def load_dataset(self, hdf):
		"""Add the local values of the feature to the hdf dataset.
		"""
		for (key, value) in self.hdf.items():
			hdf.setValue(key, str(value))
		## add the stylesheet file if it exists
		css_file = os.path.join(self.plugin_dir, self.get_name() + ".css")
		if os.path.exists(css_file):
			hdf.setValue("Data.StylesheetFiles.%s" % self.get_name(), css_file)
		


	def is_auth_required(self):
		"""check if this plugin requires authentication
		first step: check plugin configuration
		second step: check default value of plugin
		"""
		if ("requestAuth" in self.prefs) and (not self.prefs["requestAuth"] is None):
			return bool(self.prefs["requestAuth"])
		else:
			return self.request_auth


	def is_enabled(self):
		"""check if this plugin is enabled
		first step: check plugin configuration
		second step: check default value of plugin
		"""
		if ("visibility" in self.prefs) and (not self.prefs["visibility"] is None):
			return bool(self.prefs["visibility"])
		else:
			return bool(self.plugin_visibility)


	def get_rank(self):
		"""check the rank of this plugin
		first step: check plugin configuration
		second step: check default value of plugin
		"""
		if ("rank" in self.prefs) and (not self.prefs["rank"] is None):
			return int(self.prefs["rank"])
		else:
			return int(self.rank)
	

	def set_rank(self, rank):
		"""change the current rank of the plugin in plugin_conf
		'rank' should be an integer
		"""
		self.prefs["rank"] = rank
	

	def get_visibility(self):
		"""Check which visibility flags of the plugin are set.
		"""
		try:
			if self.prefs["visibility"] is None:
				return self.plugin_visibility[:]
			return self.prefs["visibility"]
		except KeyError:
			return self.plugin_visibility


	def reset(self):
		"""Reinitialize the plugin.

		This function should be called before every run
		"""
		self.hdf = {}


	def get_test_class(self):
		"""Return the unittest class of the feature.
		"""
		import imp
		pl_file = os.path.join(self.plugin_dir, "unittests.py")
		if os.access(pl_file, os.R_OK) and os.path.isfile(pl_file):
			try:
				return imp.load_source("unittests_%s" % self.get_name(), pl_file).unittests
			except AttributeError:
				pass
		try:
			self.cbox.log.info("could not load unittests for plugin: %s" % \
					self.get_name())
		except AttributeError:
			pass
		return None

