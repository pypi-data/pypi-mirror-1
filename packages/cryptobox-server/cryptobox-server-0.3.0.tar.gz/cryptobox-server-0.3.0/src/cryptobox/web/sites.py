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
""" this module handles all http requests and renders a website """

__revision__ = "$Id: sites.py 780 2007-02-06 10:08:55Z lars $"

import cryptobox.core.main
import cryptobox.web.dataset
import cryptobox.plugins.manage
import cryptobox.core.exceptions
import re
import cherrypy
import os
import sys

try:
	import neo_cgi, neo_util, neo_cs
except ImportError:
	_ERRMSG = "Could not import clearsilver module. \
			Try 'apt-get install python-clearsilver'."
	sys.stderr.write(_ERRMSG)
	raise ImportError, _ERRMSG


GETTEXT_DOMAIN = 'cryptobox-server'


class PluginIconHandler:
	"""deliver the icons of available plugins via cherrypy
	
	the state (enabled/disabled) and the require-auth setting is ignored to
	avoid repetitive reloading"""

	def __init__(self, plugins):
		for plugin in plugins.get_plugins():
			if not plugin:
				continue
			plname = plugin.get_name()
			## expose the get_icon function of this plugin
			setattr(self, plname, plugin.get_icon)



class PluginDownloadHandler:
	"""deliver downloadable files of available plugins via cherrypy
	
	the state (enabled/disabled) and the require-auth setting is ignored
	"""

	def __init__(self, plugins):
		for plugin in plugins.get_plugins():
			if not plugin:
				continue
			plname = plugin.get_name()
			## expose the get_icon function of this plugin
			setattr(self, plname, plugin.download)



class WebInterfaceSites:
	"""handle all http requests and render pages

	this includes:
	  - filtering common arguments
	  - calling feature actions
	  - translating content

	all available features are dynamically exposed
	"""

	## this template is used under strange circumstances
	defaultTemplate = "empty"


	def __init__(self, conf_file=None):
		## we should only use variables preceded by "__" to avoid name conflicts
		## when loading features
		self.cbox = cryptobox.core.main.CryptoBox(conf_file)
		self.__cached_language_data = None
		self.__dataset = None
		## load the plugin manager - we will not try to detect new plugins on
		## the fly ...
		self.__plugin_manager = cryptobox.plugins.manage.PluginManager(
				self.cbox, self.cbox.prefs["Locations"]["PluginDir"], self)
		self.__reset_dataset()
		## store the original http error handler
		self._cp_on_http_error = self.new_http_error_handler
		## set initial language order
		self.lang_order = self.cbox.prefs["WebSettings"]["Languages"][:]
		## publish plugin icons
		self.icons = PluginIconHandler(self.__plugin_manager)
		self.icons.exposed = True
		## publish plugin downloads
		self.downloads = PluginDownloadHandler(self.__plugin_manager)
		self.downloads.exposed = True
		## announce that the server started up
		self.setup()


	def setup(self):
		"""Prepare the webinterface.
		"""
		self.cbox.setup()
		for plugin in self.__plugin_manager.get_plugins():
			if plugin:
				plugin.handle_event("bootup")


	def cleanup(self):
		"""Shutdown the webinterface safely.
		"""
		self.cbox.log.info("Shutting down webinterface ...")
		for plugin in self.__plugin_manager.get_plugins():
			if plugin:
				self.cbox.log.info("Cleaning up plugin '%s' ..." % plugin.get_name())
				plugin.handle_event("shutdown")
		self.cbox.cleanup()


	def __reset_dataset(self):
		"""this method has to be called at the beginning of every "site" action
			important: only at the beginning of an action (to not loose information)
			important: for _every_ "site" action (cherrypy is stateful)
		also take care for the plugins, as they also contain datasets
		"""
		self.__load_plugins()
		self.__dataset = cryptobox.web.dataset.WebInterfaceDataset(
				self.cbox, self.cbox.prefs, self.__plugin_manager)
		## check, if a configuration partition has become available
		self.cbox.prefs.prepare_partition()


	def __load_plugins(self):
		"""reinitialize the list of available plugins

		this includes the following:
		  - reload all plugins and check their state (disabled or not)
		  - reinitilize the datasets of all plugins
		"""
		#TODO: in the long-term we should create a separate object that only
		# contains the plugin handlers - this avoids some hassle of namespace
		# conflicts - this object will be the cherrypy.server.root
		# finish this for v0.4
		for plugin in self.__plugin_manager.get_plugins():
			if not plugin:
				continue
			plname = plugin.get_name()
			## remove the old plugin handler and attach a new one
			try:
				## check if there are name conflicts: e.g. a local variable has
				## the same name as a plugin to be loaded -> skip these plugins
				## if we would not check this here, nasty effects could occour
				prev_obj = getattr(self, plname)
				if not callable(prev_obj) or not prev_obj.exposed:
					## name conflict - see below
					raise NameError
				## remove the plugin handler
				delattr(self, plname)
			except AttributeError:
				## "self" does not contain the given "plname" element
				## this is ok, as we are just cleaning up
				pass
			except NameError:
				## the attribute "exposed" of the element self."plname" does 
				## not exist - it seems, that we have a name conflict
				self.cbox.log.error("Skipping feature (%s) as its" % plname
						+ " name conflicts with a local variable - see"
						+ " module cryptobox.web.sites")
				## skip this plugin
				continue
			## the old attribute was cleaned up - we can reinitialize it now
			if plugin.is_enabled():
				self.cbox.log.info("Plugin '%s' loaded" % plname)
				## expose all features as URLs
				setattr(self, plname, self.return_plugin_action(plugin))
				getattr(self, plname).exposed = True
				#TODO: check, if the stream_response feature really works
				#for now the "stream_response" feature seems to be broken
				#setattr(getattr(self, plname), "stream_respones", True)
			else:
				self.cbox.log.info("Plugin '%s' is disabled" % plname)
				## nothing else has to be done


	## sub pages requiring authentication may not be defined above
	def __request_auth(self=None):
		""" this is a function decorator to check authentication
		"""
		def check_credentials(site):
			""" see description of _inner_wrapper - please simplify this!
			"""
			def _inner_wrapper(self, *args, **kargs):
				"""this function was necessary while trying around with the
				function decorator - if someone can implement the decorator
				with less effort, then any suggestions are welcome!
				"""
				import base64
				## define a "non-allowed" function
				user, password = None, None
				try:
					## ignore the "Basic " (first six letters) part
					resp = cherrypy.request.headers["Authorization"][6:]
					(user, password) = base64.b64decode(resp).split(":", 1)
				except KeyError:
					## no "authorization" header was sent
					pass
				except TypeError:
					## invalid base64 string
					pass
				except AttributeError:
					## no cherrypy request header defined
					pass
				auth_dict = self.cbox.prefs.user_db["admins"]
				if user in auth_dict.keys():
					if self.cbox.prefs.user_db.get_digest(password) == auth_dict[user]:
						## ok: return the choosen page
						self.cbox.log.info("access granted for: %s" % user)
						return site(self, *args, **kargs)
					else:
						self.cbox.log.info(
						        "wrong password supplied for: %s" % user)
				else:
					self.cbox.log.info("unknown user: %s" % str(user))
				## wrong credentials: return "access denied"
				cherrypy.response.headers["WWW-Authenticate"] = \
						'''Basic realm="CryptoBox"'''
				cherrypy.response.status = 401
				return self.__render("access_denied")
			return _inner_wrapper
		return check_credentials
	

	######################################################################
	## put real sites down here and don't forget to expose them at the end


	@cherrypy.expose
	def index(self, weblang="", help="0", device=None):
		"""the default page on startup - we show the list of available disks
		"""
		self.__reset_dataset()
		self.__set_web_lang(weblang)
		self.__check_environment()
		## do not forget the language!
		param_dict = {"weblang":weblang}
		## render "disks" plugin by default
		return self.return_plugin_action(
				self.__plugin_manager.get_plugin("disks"))(**param_dict)


	def new_http_error_handler(self, error_code, message):
		"""handle http errors gracefully

		404 - not found errors: ignored if url is below /cryptobox-misc/
		other 404 errors: send the error code and return a nice informative page
		500 - runtime errors: return "ok" exit code and show a polite excuse
		others: are there any other possible http errors?
		"""
		import traceback
		## we ignore uninteresting not-found errors
		if (error_code == 404) and \
				(cherrypy.request.path.startswith("/cryptobox-misc/") or \
				 cherrypy.request.path in ['/robots.txt','/favicon.ico']):
			cherrypy.response.status = error_code
			return
		## an invalid action was requested
		if error_code == 404:
			## we send a not-found error (with the usual interface)
			cherrypy.response.status = error_code
			self.__dataset["Data.Warning"] = "InvalidAction"
			cherrypy.response.body = self.__render("empty")
			return
		## are there still bugs in the code?
		if error_code == 500:
			## we fix the error code (200 is "OK")
			cherrypy.response.status = 200
			self.cbox.log.error(
					"HTTP-ERROR[500] - runtime error: %s" % str(message))
			## add a traceback and exception information to the lo
			for log_line in traceback.format_exception(*sys.exc_info()):
				self.cbox.log.error("\t%s" % log_line)
			self.__dataset["Data.Warning"] = "RuntimeError"
			cherrypy.response.body = self.__render("empty")
			return
		## unknown error type
		cherrypy.response.status = error_code
		self.cbox.log.warn("HTTP-ERROR[%d] - an unknown error occoured: %s" \
				% (error_code, message))
		cherrypy.response.body = self.__render("empty")


	def return_plugin_action(self, plugin):
		""" returns a function that is suitable for handling a cherrypy
		page request
		"""
		def handler(self, weblang="", device=None, help="0", redirect=None,
				message_keep=None, **args):
			"""this function handles a cherrypy page request
			"""
			plugin.reset()
			self.__reset_dataset()
			self.__check_environment()
			self.__set_web_lang(weblang)
			## we always read the "device" setting - otherwise volume-plugin
			## links would not work easily
			## (see "volume_props" linking to "volume_format_fs")
			## it will get ignored for non-volume plugins
			plugin.device = None
			if device and self.__set_device(device):
				plugin.device = device
			## check the device argument of volume plugins
			if "volume" in plugin.plugin_capabilities:
				## initialize the dataset of the selected device if necessary
				if plugin.device:
					self.__dataset.set_current_disk_state(plugin.device)
				else:
					## invalid (or missing) device setting
					return self.__render(self.defaultTemplate)
			## check if there is a "redirect" setting - this will override
			## the return value of the do_action function
			## (e.g. useful for umount-before-format)
			override_next_template = None
			if redirect:
				override_next_template = { "plugin": redirect }
				if "volume" in plugin.plugin_capabilities:
					override_next_template["values"] = {"device":plugin.device}
			## check for information to be kept after the last call
			if message_keep:
				for (key, value) in message_keep["dataset"].items():
					self.__dataset[key] = value
			## check if the device is busy
			if plugin.device and self.cbox.get_container(plugin.device).is_busy():
				return self.__render("volume_busy")
			## call the plugin handler
			next_template = plugin.do_action(**args)
			## for 'volume' plugins: reread the dataset of the current disk
			## additionally: set the default template for plugins
			if "volume" in plugin.plugin_capabilities:
				## maybe the state of the current volume was changed?
				self.__dataset.set_current_disk_state(plugin.device)
				if not next_template:
					next_template = { "plugin":"volume_mount",
						    "values":{"device":plugin.device}}
			else:
				## some non-volume plugins change the internal state of other
				## plugins - e.g.: plugin_manager
				## if we do not call __load_plugins now, then it is possible
				## to call a plugin directly after disabling it (only once)
				self.__load_plugins()
				self.__dataset.set_plugin_data()
				## default page for non-volume plugins is the disk selection
				if not next_template:
					next_template = { "plugin":"disks", "values":{} }
			#TODO: there is a lot of piece-by-piece updating around here
			# for v0.4 we should just call __reset_dataset - but this would
			# require to store the currently changed dataset values (e.g.i
			# weblang) somewhere else to not override it
			## some non-volume plugins may change the state of containers
			## the mount plugin may change the number of active disks - for the logo
			self.__dataset.set_containers_state()
			## was a redirect requested?
			if override_next_template:
				next_template = override_next_template
			## if another plugins was choosen for 'next_template', then do it!
			if isinstance(next_template, dict) \
					and "plugin" in next_template.keys() \
					and "values" in next_template.keys() \
					and self.__plugin_manager.get_plugin(next_template["plugin"]):
				value_dict = dict(next_template["values"])
				## force the current weblang attribute - otherwise it gets lost
				value_dict["weblang"] = self.lang_order[0]
				## check for warnings/success messages, that should be kept
				if "Data.Success" in plugin.hdf.keys() \
						or "Data.Warning" in plugin.hdf.keys():
					value_dict["message_keep"] = {"plugin":plugin, "dataset":{}}
					for keep_key in ("Data.Warning", "Data.Success"):
						if keep_key in plugin.hdf.keys():
							self.cbox.log.info("keeping message: %s" % \
									plugin.hdf[keep_key])
							value_dict["message_keep"]["dataset"][keep_key] = \
						            plugin.hdf[keep_key]
				new_plugin = self.__plugin_manager.get_plugin(next_template["plugin"])
				return self.return_plugin_action(new_plugin)(**value_dict)
			## save the currently active plugin name
			self.__dataset["Data.ActivePlugin"] = plugin.get_name()
			return self.__render(next_template, plugin)
		## apply authentication?
		if plugin.is_auth_required():
			return lambda **args: self.__request_auth()(handler)(self, **args)
		else:
			return lambda **args: handler(self, **args)

	
	@cherrypy.expose
	def test(self, weblang="", help="0", device=None):
		"""test authentication - this function may be safely removed
		"""
		self.__reset_dataset()
		self.__set_web_lang(weblang)
		self.__check_environment()
		result = "<html><head><title>Test</title><body><ul>"
		for key in cherrypy.request.headers:
			result += "<li>%s - %s</li>" % (str(key), str(cherrypy.request.headers[key]))
		result += "</ul></body></html>"
		return result
	

	@cherrypy.expose
	def test_stream(self, weblang="", help="0", device=None):
		"""just for testing purposes - to check if the "stream_response" feature
		actually works - for now (September 02006) it does not seem to be ok
		"""
		import time
		yield "<html><head><title>neu</title></head><body><p><ul>"
		for num in range(10):
			yield "<li>yes: %d - %s</li>" % (num, str(time.time()))
			time.sleep(1)
		yield "</ul></p></html>"



	##################### input checker ##########################

	def __check_environment(self):
		"""inform the user of suspicious environmental problems

		examples are: non-https, readonly-config, ...
		"""
		warnings = []
		for pl in self.__plugin_manager.get_plugins():
			warnings.extend(pl.get_warnings())
		warnings.sort(reverse=True)
		for (index, (warn_prio, warn_text)) in enumerate(warnings):
			self.__dataset["Data.EnvironmentWarning.%d" % index] = warn_text


	def __set_web_lang(self, value):
		"""set the preferred priority of languages according to this order:
			1. language selected via web interface
			2. preferred browser language setting
			3. languages defined in the config file
		"""
		## start with the configured language order
		lang_order = self.cbox.prefs["WebSettings"]["Languages"][:]
		self.cbox.log.debug(
				"updating language preferences (default: %s)" % str(lang_order))
		## put the preferred browser language in front
		guess = self.__get_browser_language(lang_order)
		if guess:
			lang_order.remove(guess)
			lang_order.insert(0, guess)
			self.cbox.log.debug(
					"raised priority of preferred browser language: %s" % guess)
		## check if the 'weblang' setting is necessary (does it change the result
		## of the language preference calculation?)
		override_by_weblang = False
		## is the chosen language (via web interface) valid? - put it in front
		if value and (value in lang_order) and (not re.search(r'\W', value)):
			## skip if the 'weblang' value is already at the top of the list
			if lang_order.index(value) != 0:
				override_by_weblang = True
				lang_order.remove(value)
				lang_order.insert(0, value)
				self.cbox.log.debug(
					"raised priority of selected language: %s" % value)
		elif value:
			self.cbox.log.info("invalid language selected: %s" % value)
		## store current language setting
		self.cbox.log.info(
				"current language preference: %s" % str(lang_order))
		self.lang_order = lang_order
		self.__dataset["Settings.Language"] = lang_order[0]
		## we do not have to add the LinkAttr if it is irrelevant
		if override_by_weblang:
			self.__dataset["Settings.LinkAttrs.weblang"] = lang_order[0]


	def __get_browser_language(self, avail_langs):
		"""guess the preferred language of the user (as sent by the browser)
		take the first language, that is part of 'avail_langs'
		"""
		try:
			pref_lang_header = cherrypy.request.headers["Accept-Language"]
		except KeyError:
			## no language header was specified
			return None
		## this could be a typical 'Accept-Language' header:
		##   de-de,de;q=0.8,en-us;q=0.5,en;q=0.3
		regex = re.compile(r"\w+(-\w+)?(;q=[\d\.]+)?$")
		pref_langs = [e.split(";", 1)[0]
			for e in pref_lang_header.split(",")
			if regex.match(e)]
		## is one of these preferred languages available?
		for lang in pref_langs:
			if lang in avail_langs:
				return lang
		## we try to be nice: also look for "de" if "de-de" was specified ...
		for lang in pref_langs:
			## use only the first part of the language
			short_lang = lang.split("-", 1)[0]
			if short_lang in avail_langs:
				return short_lang
		## we give up
		return None


	def __set_device(self, device):
		"""check a device name that was chosen via the web interface
		issue a warning if the device is invalid"""
		if device and re.match(r'[\w /\-]+$', device) \
				and self.cbox.get_container(device):
			self.cbox.log.debug("Select device: %s" % device)
			return True
		else:
			self.cbox.log.warn("Invalid device: %s" % device)
			self.__dataset["Data.Warning"] = "InvalidDevice"
			return False
	

	def __substitute_gettext(self, languages, text_domain, hdf):
		"""substitute all texts in the hdf dataset with their translated
		counterparts as returned by gettext
		"""
		import gettext
		try:
			translator = gettext.translation(text_domain, languages=languages)
		except IOError, err_msg:
			## no translation found
			self.cbox.log.warn("unable to load language file: %s" % err_msg)
			return hdf
		def walk_tree(parent_name, hdf_node):
			"""iterate through all nodes"""
			def translate_node(node):
				"""turn one single string into unicode"""
				if not node.value():
					return
				for (key, value) in node.attrs():
					## ignore all nodes with the 'LINK' attribute
					## for now clearsilver is buggy regarding attributes
					## buggy -> parsing of a hdf file fails silently
					if key == "LINK":
						return
				## as long as the attributes do not work, we have to rely on
				## some magic names to ignore translations
				if (parent_name == "Link") and \
						(node.name() in ["Rel", "Prot", "Abs"]):
					return
				try:
					#TODO: we should use unicode - or not? - turn it on later
					#node.setValue("", translator.ugettext(node.value()))
					## quite obscure: ugettext can handle None - gettext breaks instead
					node.setValue("", translator.gettext(node.value()))
				except UnicodeEncodeError, err_msg:
					self.cbox.log.info(
						    "Failed unicode encoding for gettext: %s - %s" \
						    % (node.value(),err_msg))
					## fallback to default encoding
					node.setValue("", translator.gettext(node.value()))
			while hdf_node:
				translate_node(hdf_node)
				walk_tree(hdf_node.name(), hdf_node.child())
				hdf_node = hdf_node.next()
		walk_tree("", hdf)


	def __get_language_data(self):
		"""return the hdf dataset of the main interface and all plugins
		translations are done according to self.lang_order
		"""
		## check if the language setting has changed - use cache if possible
		if self.__cached_language_data and \
				self.__cached_language_data["lang_order"] == self.lang_order:
			self.cbox.log.debug(
					"using cached language data: %s" % str(self.lang_order))
			return self.__cached_language_data["hdf"]
		self.cbox.log.debug("generating language data")
		hdf = neo_util.HDF()
		hdf.readFile(os.path.join(
				self.cbox.prefs["Locations"]["TemplateDir"],"language.hdf"))
		self.__substitute_gettext(self.lang_order, GETTEXT_DOMAIN, hdf)
		## load the language data of all plugins
		for plugin in self.__plugin_manager.get_plugins():
			pl_lang = plugin.get_language_data()
			self.__substitute_gettext(self.lang_order, "%s-feature-%s" % \
					(GETTEXT_DOMAIN, plugin.get_name()), pl_lang)
			hdf.copy("Plugins.%s" % plugin.get_name(), pl_lang)
			self.cbox.log.debug(
					"language data for plugin loaded: %s" % plugin.get_name())
		## cache result for later retrieval
		self.__cached_language_data = \
				{"lang_order": self.lang_order, "hdf": hdf}
		return hdf


	def __render(self, render_info, plugin=None):
		'''renders from clearsilver templates and returns the resulting html
		'''
		## is render_info a string (filename of the template) or a dictionary?
		if isinstance(render_info, dict):
			template = render_info["template"]
			if render_info.has_key("generator"):
				generator = render_info["generator"]
			else:
				generator = None
		else:
			(template, generator) = (render_info, None)

		## load the language data
		hdf = neo_util.HDF()
		hdf.copy("Lang", self.__get_language_data())

		## first: assume, that the template file is in the global
		## template directory
		self.__dataset["Settings.TemplateFile"] = os.path.abspath(os.path.join(
				self.cbox.prefs["Locations"]["TemplateDir"],
				template + ".cs"))

		if plugin:
			## check, if the plugin provides the template file -> overriding
			plugin_cs_file = plugin.get_template_filename(template)
			if plugin_cs_file:
				self.__dataset["Settings.TemplateFile"] = plugin_cs_file

			## add the current state of the plugins to the hdf dataset
			self.__dataset["Data.Status.Plugins.%s" % plugin.get_name()] = \
					plugin.get_status()
			## load the dataset of the plugin
			plugin.load_dataset(hdf)

		self.cbox.log.info("rendering site: " + template)

		cs_path = os.path.abspath(os.path.join(
				self.cbox.prefs["Locations"]["TemplateDir"], "main.cs"))
		if not os.access(cs_path, os.R_OK):
			self.cbox.log.error(
					"Couldn't read clearsilver file: %s" % cs_path)
			yield "Couldn't read clearsilver file: %s" % cs_path
			return

		self.cbox.log.debug(self.__dataset)
		for key in self.__dataset.keys():
			hdf.setValue(key, str(self.__dataset[key]))
		cs_data = neo_cs.CS(hdf)
		cs_data.parseFile(cs_path)

		## is there a generator containing additional information?
		if not generator:
			## all content in one flush
			result_data = cs_data.render().splitlines()
			## remove empty leading lines (avoids html warnings)
			while not result_data[0].strip():
				del result_data[0]
			yield "\n".join(result_data)
		else:
			content_generate = generator()
			dummy_line = """<!-- CONTENT_DUMMY -->"""
			## now we do it linewise - checking for the content marker
			for line in cs_data.render().splitlines():
				if line.find(dummy_line) != -1:
					yield line.replace(dummy_line, content_generate.next())
				else:
					yield line + "\n"

