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
	
	def test_get_date(self):
		"""retrieve the current date"""
		date = self._get_current_date()
	

	def test_change_date(self):
		"""set the date back and forth"""
		now = self._get_current_date()
		## copy current time
		new_date = dict(now)
		## move three minutes forward (more is not nice because of screensavers)
		new_date["minute"] = (now["minute"] + 3) % 60
		## in case of minute-overflow we also have to move the hour a little bit forward
		new_date["hour"] = now["hour"] + ((now["minute"] + 3) / 60)
		## move forward ...
		self._setDate(new_date)
		self.assertEquals(new_date, self._get_current_date())
		## ... and backward
		self._setDate(now)
		self.assertEquals(now, self._get_current_date())
	

	def test_try_broken_date(self):
		"""expect error messages for invalid dates"""
		self._setDate({"hour":12, "minute":40, "year":2004, "month":7, "day":0})
		self.cmd.find("invalid value for date")
		self._setDate({"hour":12, "minute":40, "year":"x", "month":7, "day":2})
		self.cmd.find("invalid value for date")
		self._setDate({"hour":12, "minute":40, "year":2004, "month":2, "day":31})
		self.cmd.find("invalid value for date")


	def _get_current_date(self):
		date_url = self.url + "date"
		self.register_auth(date_url)
		self.cmd.go(date_url)
		self.cmd.find("Data.Status.Plugins.date=([0-9]+/[0-9]+/[0-9]+/[0-9]+/[0-9]+/[0-9]+)$", "m")
		dateNumbers = self.locals["__match__"].split("/")
		self.assertEquals(len(dateNumbers), 6)
		## we ignore seconds
		dateField = {
			"year"	: int(dateNumbers[0]),
			"month"	: int(dateNumbers[1]),
			"day"	: int(dateNumbers[2]),
			"hour"	: int(dateNumbers[3]),
			"minute"	: int(dateNumbers[4])}
		return dateField
	

	def _setDate(self, date):
		"""for now we have to use this function instead of the one below"""
		date_url = self.url + "date?weblang=en&store=1&year=%s&month=%s&day=%s&hour=%s&minute=%s"\
			% (str(date["year"]), str(date["month"]), str(date["day"]),
				str(date["hour"]), str(date["minute"]))
		self.register_auth(date_url)
		self.cmd.go(date_url)


	def _setDateBroken(self, date):
		"""this should work, but the parsing of twill seems to be broken
		as soon as the twill bug is fixed, we should use this function"""
		date_url = self.url + "date"
		self.register_auth(date_url)
		self.cmd.go(date_url)
		self.cmd.formvalue("set_date", "year", str(date["year"]))
		self.cmd.formvalue("set_date", "month", str(date["month"]))
		self.cmd.formvalue("set_date", "day", str(date["day"]))
		self.cmd.formvalue("set_date", "hour", str(date["hour"]))
		self.cmd.formvalue("set_date", "minute", str(date["minute"]))
		self.cmd.submit()

