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

"""Change date and time.

requires:
 - date
 - ntpdate (planned)
"""

__revision__ = "$Id"

import cryptobox.plugins.base


class date(cryptobox.plugins.base.CryptoBoxPlugin):
	"""The date feature of the CryptoBox.
	"""

	plugin_capabilities = [ "system" ]
	plugin_visibility = [ "preferences" ]
	request_auth = False
	rank = 10

	def do_action(self, store=None, year=0, month=0, day=0, hour=0, minute=0):
		"""The action handler.
		"""
		import datetime
		if store:
			try:
				year, month, day = int(year), int(month), int(day)
				hour, minute = int(hour), int(minute)
				## check if the values are valid
				datetime.datetime(year, month, day, hour, minute)
			except ValueError:
				self.hdf["Data.Warning"] = "Plugins.date.InvalidDate"
			else:
				new_date = "%02d%02d%02d%02d%d" % (month, day, hour, minute, year)
				if self.__set_date(new_date):
					self.cbox.log.info("changed date to: %s" % new_date)
					self.hdf["Data.Success"] = "Plugins.date.DateChanged"
				else:
					## a failure should usually be an invalid date (we do not check it really)
					self.cbox.log.info("failed to set date: %s" % new_date)
					self.hdf["Data.Warning"] = "Plugins.date.InvalidDate"
		self.__prepare_form_data()
		return "form_date"


	def get_status(self):
		"""Retrieve the status of the feature.
		"""
		now = self.__get_current_date()
		return "%d/%d/%d/%d/%d/%d" % \
				(now.year, now.month, now.day, now.hour, now.minute, now.second)


	def get_warnings(self):
		import os
		warnings = []
		if not os.path.isfile(self.root_action.DATE_BIN):
			warnings.append((48, "Plugins.%s.MissingProgramDate" % self.get_name()))
		return warnings


	def __prepare_form_data(self):
		"""Set some hdf values.
		"""
		cur_date = self.__get_current_date()
		self.hdf[self.hdf_prefix + "year"]	= cur_date.year
		self.hdf[self.hdf_prefix + "month"]	= cur_date.month
		self.hdf[self.hdf_prefix + "day"]	= cur_date.day
		self.hdf[self.hdf_prefix + "hour"]	= cur_date.hour
		self.hdf[self.hdf_prefix + "minute"]	= cur_date.minute


	def __get_current_date(self):
		"""Retrieve the current date and time.
		"""
		import datetime
		return datetime.datetime(2000, 1, 1).now()
	

	def __set_date(self, new_date):
		"""Set a new date and time.
		"""
		import subprocess
		import os
		proc = subprocess.Popen(
			shell = False,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"plugin",
				os.path.join(self.plugin_dir, "root_action.py"),
				new_date])
		proc.wait()
		return proc.returncode == 0

