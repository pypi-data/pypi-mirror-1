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


"""The logs feature of the CryptoBox.
"""

__revision__ = "$Id"

import cryptobox.plugins.base
import re
import datetime
import cherrypy

LOG_LEVELS = [ 'DEBUG', 'INFO', 'NOTICE', 'WARNING', 'ERROR' ]

LINE_REGEX = re.compile(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) " \
		+ r"(?P<hour>\d{2}):(?P<minute>\d{2}):\d{2},\d{3} (?P<level>" \
		+ "|".join([ "(?:%s)" % e for e in LOG_LEVELS]) + r"): (?P<text>.*)$")

class logs(cryptobox.plugins.base.CryptoBoxPlugin):
	"""The logs feature of the CryptoBox.
	"""

	plugin_capabilities = [ "system" ]
	plugin_visibility = [ "preferences" ]
	request_auth = False
	rank = 90

	def do_action(self, lines=50, size=3000, level=None):
		"""Show the latest part of the log file.
		"""
		## filter input
		try:
			lines = int(lines)
			if lines <= 0:
				raise(ValueError)
		except ValueError:
			self.cbox.log.info("[logs] invalid line number: %s" % str(lines))
			lines = 50
		try:
			size = int(size)
			if size <= 0:
				raise(ValueError)
		except ValueError:
			self.cbox.log.info("[logs] invalid log size: %s" % str(size))
			size = 3000
		if not level is None:
			level = str(level)
			if not level in LOG_LEVELS:
				self.cbox.log.info("[logs] invalid log level: %s" % str(level))
				level = None
		for (index, line) in enumerate(self.__filter_log_content(lines, size, level)):
			self.__set_line_hdf_data(self.hdf_prefix + "Content.%d" % index, line)
		self.hdf[self.hdf_prefix + "Destination"] = \
				self.cbox.prefs["Log"]["Destination"].lower()
		return "show_log"


	@cherrypy.expose
	def download(self, **kargs):
		"""Download the complete log file

		**kargs are necessary - we have to ignore 'weblang' and so on ...
		"""
		log_file = self.__get_log_destination_file()
		if log_file is None:
			return ""
		else:
			return cherrypy.lib.cptools.serveFile(log_file,
					disposition="attachment", name="cryptobox_logfile.txt")


	def get_status(self):
		"""The current status includes the log configuration details.
		"""
		return "%s:%s:%s" % (
			self.cbox.prefs["Log"]["Level"],
			self.cbox.prefs["Log"]["Destination"],
			self.cbox.prefs["Log"]["Details"])
	

	def __filter_log_content(self, lines, max_size, level):
		"""Filter, sort and shorten the log content.
		"""
		if level and level in LOG_LEVELS:
			filtered_levels = LOG_LEVELS[:]
			## only the given and higher levels are accepted
			while filtered_levels[0] != level:
				del filtered_levels[0]
			content = []
			current_length = 0
			for line in self.__get_log_data():
				## search for matching lines for the given log level
				for one_level in filtered_levels:
					if line.find(" %s: " % one_level) != -1:
						break
				else:
					## the line does not contain an appropriate level name
					continue
				## we found a line that fits
				content.append(line)
				current_length += len(line)
				if lines and len(content) >= lines:
					break
				if max_size and current_length >= max_size:
					break
		else:
			content = self.__get_log_data(lines, max_size)
		return content


	def __set_line_hdf_data(self, hdf_prefix, line):
		"""Parse the log line for time and log level.

		If parsing fails, then the output line is simply displayed without
		meta information.
		"""
		self.hdf[hdf_prefix + ".Text"] = line.strip()
		match = LINE_REGEX.match(line)
		if not match:
			## we could not parse the line - just return the text without meta info
			return
		## matching was successful - we can parse the line for details
		## calculate time difference of log line (aka: age of event)
		try:
			(year, month, day, hour, minute) = match.group(
					'year', 'month', 'day', 'hour', 'minute')
			(year, month, day, hour, minute) = \
					(int(year), int(month), int(day), int(hour), int(minute))
			## timediff is a timedelta object
			timediff = datetime.datetime.today() - \
					datetime.datetime(year, month, day, hour, minute)
			## the time units (see below) correspond to the names within the language
			## file: Text.TimeUnits.Days ...
			if timediff.days >= 1:
				self.hdf[hdf_prefix + ".TimeDiff.Unit"] = 'Days'
				self.hdf[hdf_prefix + ".TimeDiff.Value"] = timediff.days
			elif timediff.seconds >= 3600:
				self.hdf[hdf_prefix + ".TimeDiff.Unit"] = 'Hours'
				self.hdf[hdf_prefix + ".TimeDiff.Value"] = timediff.seconds / 3600
			elif timediff.seconds >= 60:
				self.hdf[hdf_prefix + ".TimeDiff.Unit"] = 'Minutes'
				self.hdf[hdf_prefix + ".TimeDiff.Value"] = timediff.seconds / 60
			else:
				self.hdf[hdf_prefix + ".TimeDiff.Unit"] = 'Seconds'
				self.hdf[hdf_prefix + ".TimeDiff.Value"] = timediff.seconds
		except (OverflowError, TypeError, ValueError, IndexError), err_msg:
			pass
		## retrieve the level
		try:
			self.hdf[hdf_prefix + ".Level"] = match.group('level')
		except IndexError:
			pass
		try:
			self.hdf[hdf_prefix + ".Text"] = match.group('text').strip()
		except IndexError:
			pass
	

	def __get_log_destination_file(self):
		"""For non-file log destinations return 'None' and output a warning
		"""
		try:
			if self.cbox.prefs["Log"]["Destination"].upper() == "FILE":
				import os
				return os.path.abspath(self.cbox.prefs["Log"]["Details"])
			else:
				return None
		except KeyError:
			self.cbox.log.error(
					"could not evaluate one of the following config settings: "
					+ "[Log]->Destination or [Log]->Details")
			return None


	def __get_log_data(self, lines=None, max_size=None):
		"""get the most recent log entries of the log file

		the maximum number and size of these entries can be limited by
		'lines' and 'max_size'
		"""
		log_file = self.__get_log_destination_file()
		## return nothing if the currently selected log output is not a file
		if log_file is None:
			return []
		try:
			fdesc = open(log_file, "r")
			if max_size:
				fdesc.seek(-max_size, 2)	# seek relative to the end of the file
			content = fdesc.readlines()
			fdesc.close()
		except IOError:
			self.cbox.log.warn("failed to read the log file (%s)" % log_file)
			return []
		if lines:
			content = content[-lines:]
		content.reverse()
		return content


