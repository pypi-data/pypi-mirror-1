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

"""The help feature of the CryptoBox.
"""

__revision__ = "$Id"

import cryptobox.plugins.base

class help(cryptobox.plugins.base.CryptoBoxPlugin):
	"""The help feature of the CryptoBox.
	"""

	#plugin_capabilities = [ "system" ]
	#TODO: enable this plugin as soon as the user documentation is ready again
	plugin_capabilities = [ ]
	plugin_visibility = [ "menu" ]
	request_auth = False
	rank = 80

	default_lang = 'en'
	default_page = "CryptoBoxUser"

	def do_action(self, page=""):
		'''prints the offline wikipage
		'''
		import re, os
		## check for invalid characters and if the page exists in the default language
		if page and \
				not re.search(r'\W', page) and \
				os.path.isfile(os.path.join(self.cbox.prefs["Locations"]["DocDir"],
						self.default_lang, page + '.html')):
			## everything is ok
			pass
		else:
			## display this page as default help page
			page = self.default_page
			if page:
				## issue warning
				self.cbox.log.info("could not find the selected documentation page: %s" % str(page))
		## store the name of the page
		self.hdf[self.hdf_prefix + "Page"] = page
		## choose the right language
		for lang in self.site.lang_order:
			if os.path.isfile(os.path.join(self.cbox.prefs["Locations"]["DocDir"],
					lang, page + '.html')):
				doc_lang = lang
				break
		else:
			doc_lang = self.default_lang
		self.hdf[self.hdf_prefix + "Language"] = doc_lang
		## store the current setting for a later "getStatus" call
		self.current_lang = doc_lang
		self.current_page = page
		return "doc"


	def get_status(self):
		"""Retrieve the current status of the feature.
		"""
		return "%s:%s" % (self.current_lang, self.current_page)


