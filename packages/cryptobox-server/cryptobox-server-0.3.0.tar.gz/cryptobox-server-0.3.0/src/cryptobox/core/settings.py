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

"""Manage the configuration of a CryptoBox
"""

__revision__ = "$Id"

from cryptobox.core.exceptions import *
import logging
import subprocess
import os
import configobj, validate
import syslog


CONF_LOCATIONS = [
	"./cryptobox.conf",
	"~/.cryptobox.conf",
	"/etc/cryptobox-server/cryptobox.conf"]

VOLUMESDB_FILE = "cryptobox_volumes.db"
PLUGINCONF_FILE = "cryptobox_plugins.conf"
USERDB_FILE = "cryptobox_users.db"


class CryptoBoxSettings:
	"""Manage the various configuration files of the CryptoBox
	"""

	def __init__(self, config_file=None):
		self.__is_initialized = False
		self.log = logging.getLogger("CryptoBox")
		config_file = self.__get_config_filename(config_file)
		self.log.info("loading config file: %s" % config_file)
		self.prefs = self.__get_preferences(config_file)
		if not "PluginSettings" in self.prefs:
			self.prefs["PluginSettings"] = {}
		self.__validate_config()
		self.__configure_log_handler()
		self.__check_unknown_preferences()
		self.prepare_partition()
		self.volumes_db = self.__get_volumes_database()
		self.plugin_conf = self.__get_plugin_config()
		self.user_db = self.__get_user_db()
		self.misc_files = []
		self.reload_misc_files()
		self.__is_initialized = True
	

	def reload_misc_files(self):
		"""Call this method after creating or removing a 'misc' configuration file
		"""
		self.misc_files = self.__get_misc_files()
	

	def write(self):
		"""
		write all local setting files including the content of the "misc" subdirectory
		"""
		status = True
		try:
			self.volumes_db.write()
		except IOError:
			self.log.warn("Could not save the volume database")
			status = False
		try:
			self.plugin_conf.write()
		except IOError:
			self.log.warn("Could not save the plugin configuration")
			status = False
		try:
			self.user_db.write()
		except IOError:
			self.log.warn("Could not save the user database")
			status = False
		for misc_file in self.misc_files:
			if not misc_file.save():
				self.log.warn("Could not save a misc setting file (%s)" % misc_file.filename)
				status = False
		return status


	def get_misc_config_filename(self, name):
		"""Return an absolute filename for a given filename 'name'

		'name' should not contain slashes (no directory part!)
		"""
		return os.path.join(self.prefs["Locations"]["SettingsDir"], "misc", name)
	

	def create_misc_config_file(self, name, content):
		"""Create a new configuration file in the 'settings' directory

		"name" should be the basename (without a directory)
		"content" will be directly written to the file
		this method may throw an IOException
		"""
		misc_conf_file = self.get_misc_config_filename(name)
		misc_conf_dir = os.path.dirname(misc_conf_file)
		if not os.path.isdir(misc_conf_dir):
			try:
				os.mkdir(misc_conf_dir)
			except OSError, err_msg:
				## the caller expects only IOError
				raise IOError, err_msg
		cfile = open(misc_conf_file, "w")
		try:
			cfile.write(content)
		except IOError:
			cfile.close()
			raise
		cfile.close()
		## reread all misc files automatically - this should be ok
		self.reload_misc_files()


	def requires_partition(self):
		return bool(self.prefs["Main"]["UseConfigPartition"])
	

	def get_active_partition(self):
		"""Return the currently active cnfiguration partition.
		"""
		settings_dir = self.prefs["Locations"]["SettingsDir"]
		if not os.path.ismount(settings_dir):
			return None
		for line in file("/proc/mounts"):
			fields = line.split(" ")
			mount_dir = fields[1]
			fs_type = fields[2]
			if fs_type == "tmpfs":
				## skip ramdisks - these are not really "active partitions"
				continue
			try:
				if os.path.samefile(mount_dir, settings_dir):
					return fields[0]
			except OSError:
				pass
		## no matching entry found
		return None


	def mount_partition(self):
		"""Mount a config partition.
		"""
		self.log.debug("trying to mount configuration partition")
		if not self.requires_partition():
			self.log.warn("mountConfigPartition: configuration partition is "
					+ "not required - mounting anyway")
		if self.get_active_partition():
			self.log.warn("mountConfigPartition: configuration partition already "
					+ "mounted - not mounting again")
			return False
		conf_partitions = self.get_available_partitions()
		mount_dir = self.prefs["Locations"]["SettingsDir"]
		if not conf_partitions:
			## return, if tmpfs is already mounted
			if os.path.ismount(mount_dir):
				self.log.info("A ramdisk seems to be already mounted as a config " \
						+ "partition - doing nothing ...")
				## return without any actions
				return True
			self.log.warn("no configuration partition found - you have to create "
					+ "it first")
			## mount tmpfs instead to provide a place for storing stuff
			## "_tmpfs_" as parameter for mount is interpreted as a magic word
			## by CryptoBoxRootActions
			proc = subprocess.Popen(
				shell = False,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE,
				args = [
					self.prefs["Programs"]["super"],
					self.prefs["Programs"]["CryptoBoxRootActions"],
					"mount",
					"_tmpfs_",
					mount_dir ])
			(stdout, stderr) = proc.communicate()
			if proc.returncode != 0:
				self.log.error("Failed to mount a ramdisk for storing settings: %s" \
						% stderr)
				return False
			self.log.info("Ramdisk (tmpfs) mounted as config partition ...")
		else:
			partition = conf_partitions[0]
			## umount tmpfs in case it is active
			if os.path.ismount(mount_dir):
				self.umount_partition()
			proc = subprocess.Popen(
				shell = False,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE,
				args = [
					self.prefs["Programs"]["super"],
					self.prefs["Programs"]["CryptoBoxRootActions"],
					"mount",
					partition,
					mount_dir ])
			(stdout, stderr) = proc.communicate()
			if proc.returncode != 0:
				self.log.error("Failed to mount the configuration partition (%s): %s" % \
						(partition, stderr))
				return False
			self.log.info("configuration partition mounted: %s" % partition)
		## write config files (not during first initialization of this object)
		if self.__is_initialized:
			self.write()
		return True


	def umount_partition(self):
		"""Umount the currently active configuration partition.
		"""
		mount_dir = self.prefs["Locations"]["SettingsDir"]
		if not os.path.ismount(mount_dir):
			self.log.warn("umountConfigPartition: no configuration partition mounted")
			return False
		self.reload_misc_files()
		proc = subprocess.Popen(
			shell = False,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.prefs["Programs"]["super"],
				self.prefs["Programs"]["CryptoBoxRootActions"],
				"umount",
				mount_dir ])
		(stdout, stderr) = proc.communicate()
		if proc.returncode != 0:
			self.log.error("Failed to unmount the configuration partition: %s" % stderr)
			return False
		self.log.info("configuration partition unmounted")
		return True
		

	def get_available_partitions(self):
		"""returns a sequence of found config partitions"""
		self.log.debug("Retrieving available configuration partitions ...")
		proc = subprocess.Popen(
			shell = False,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.prefs["Programs"]["blkid"],
				"-c", os.path.devnull,
				"-t", "LABEL=%s" % self.prefs["Main"]["ConfigVolumeLabel"] ])
		(output, error) = proc.communicate()
		if proc.returncode == 2:
			self.log.info("No configuration partitions found")
			return []
		elif proc.returncode == 4:
			self.log.warn("Failed to call 'blkid' for unknown reasons.")
			return []
		elif proc.returncode == 0:
			if output:
				return [e.strip().split(":", 1)[0] for e in output.splitlines()]
			else:
				return []
		else:
			self.log.warn("Unknown exit code of 'blkid': %d - %s" \
					% (proc.returncode, error))

	
	def prepare_partition(self):
		"""Mount a config partition if necessary.
		"""
		if self.requires_partition() and not self.get_active_partition():
			self.mount_partition()


	def __getitem__(self, key):
		"""redirect all requests to the 'prefs' attribute"""
		return self.prefs[key]


	def __get_preferences(self, config_file):
		"""Load the CryptoBox configuration.
		"""
		import StringIO
		config_rules = StringIO.StringIO(self.validation_spec)
		try:
			prefs = configobj.ConfigObj(config_file, configspec=config_rules)
			if prefs:
				self.log.info("found config: %s" % prefs.items())
			else: 
				raise CBConfigUnavailableError(
						"failed to load the config file: %s" % config_file)
		except IOError:
			raise CBConfigUnavailableError(
					"unable to open the config file: %s" % config_file)
		return prefs


	def __validate_config(self):
		"""Check the configuration settings and cast value types.
		"""
		result = self.prefs.validate(CryptoBoxSettingsValidator(), preserve_errors=True)
		error_list = configobj.flatten_errors(self.prefs, result)
		if not error_list:
			return
		error_msgs = []
		for sections, key, text in error_list:
			section_name = "->".join(sections)
			if not text:
				error_msg = "undefined configuration value (%s) in section '%s'" % \
						(key, section_name)
			else:
				error_msg = "invalid configuration value (%s) in section '%s': %s" % \
						(key, section_name, text)
			error_msgs.append(error_msg)
		raise CBConfigError, "\n".join(error_msgs)


	def __check_unknown_preferences(self):
		"""Check the configuration file for unknown settings to avoid spelling mistakes.
		"""
		import StringIO
		config_rules = configobj.ConfigObj(StringIO.StringIO(self.validation_spec),
				list_values=False)
		self.__recursive_section_check("", self.prefs, config_rules)
		
	
	def __recursive_section_check(self, section_path, section_config, section_rules):
		"""should be called by '__check_unknown_preferences' for every section
		sends a warning message to the logger for every undefined (see validation_spec)
		configuration setting
		"""
		for section in section_config.keys():
			element_path = section_path + section
			if section in section_rules.keys():
				if isinstance(section_config[section], configobj.Section):
					if isinstance(section_rules[section], configobj.Section):
						self.__recursive_section_check(element_path + "->",
								section_config[section], section_rules[section])
					else:
						self.log.warn("configuration setting should be a value "
								+ "instead of a section name: %s" % element_path)
				else:
					if not isinstance(section_rules[section], configobj.Section):
						pass	# good - the setting is valid
					else:
						self.log.warn("configuration setting should be a section "
								+ "name instead of a value: %s" % element_path)
			elif element_path.startswith("PluginSettings->"):
				## ignore plugin settings
				pass
			else:
				self.log.warn("unknown configuration setting: %s" % element_path)


	def __get_plugin_config(self):
		"""Load the plugin configuration file if it exists.
		"""
		import StringIO
		plugin_rules = StringIO.StringIO(self.pluginValidationSpec)
		try:
			try:
				plugin_conf_file = os.path.join(
						self.prefs["Locations"]["SettingsDir"], PLUGINCONF_FILE)
			except KeyError:
				raise CBConfigUndefinedError("Locations", "SettingsDir")
		except SyntaxError:
			raise CBConfigInvalidValueError("Locations", "SettingsDir", plugin_conf_file,
					"failed to interprete the filename of the plugin config file "
					+ "correctly (%s)" % plugin_conf_file)
		## create plugin_conf_file if necessary
		if os.path.exists(plugin_conf_file):
			plugin_conf = configobj.ConfigObj(plugin_conf_file, configspec=plugin_rules)
		else:
			try:
				plugin_conf = configobj.ConfigObj(plugin_conf_file,
						configspec=plugin_rules, create_empty=True)
			except IOError:
				plugin_conf = configobj.ConfigObj(configspec=plugin_rules)
				plugin_conf.filename = plugin_conf_file
		## validate and convert values according to the spec
		plugin_conf.validate(validate.Validator())
		return plugin_conf


	def __get_volumes_database(self):
		"""Load the volume database file if it exists.
		"""
		#TODO: add configuration specification and validation
		try:
			try:
				conf_file = os.path.join(
						self.prefs["Locations"]["SettingsDir"], VOLUMESDB_FILE)
			except KeyError:
				raise CBConfigUndefinedError("Locations", "SettingsDir")
		except SyntaxError:
			raise CBConfigInvalidValueError("Locations", "SettingsDir", conf_file,
					"failed to interprete the filename of the volume database "
					+ "correctly (%s)" % conf_file)
		## create conf_file if necessary
		if os.path.exists(conf_file):
			conf = configobj.ConfigObj(conf_file)
		else:
			try:
				conf = configobj.ConfigObj(conf_file, create_empty=True)
			except IOError:
				conf = configobj.ConfigObj()
				conf.filename = conf_file
		return conf


	def __get_user_db(self):
		"""Load the user database file if it exists.
		"""
		import StringIO, sha
		user_db_rules = StringIO.StringIO(self.userDatabaseSpec)
		try:
			try:
				user_db_file = os.path.join(
						self.prefs["Locations"]["SettingsDir"], USERDB_FILE)
			except KeyError:
				raise CBConfigUndefinedError("Locations", "SettingsDir")
		except SyntaxError:
			raise CBConfigInvalidValueError("Locations", "SettingsDir", user_db_file,
					"failed to interprete the filename of the users database file "
					+ "correctly (%s)" % user_db_file)
		## create user_db_file if necessary
		if os.path.exists(user_db_file):
			user_db = configobj.ConfigObj(user_db_file, configspec=user_db_rules)
		else:
			try:
				user_db = configobj.ConfigObj(user_db_file,
						configspec=user_db_rules, create_empty=True)
			except IOError:
				user_db = configobj.ConfigObj(configspec=user_db_rules)
				user_db.filename = user_db_file
		## validate and set default value for "admin" user
		user_db.validate(validate.Validator())
		## define password hash function - never use "sha" directly - SPOT
		user_db.get_digest = lambda password: sha.new(password).hexdigest()
		return user_db


	def __get_misc_files(self):
		"""Load miscelleanous configuration files.

		e.g.: an ssl certificate, ...
		"""
		misc_dir = os.path.join(self.prefs["Locations"]["SettingsDir"], "misc")
		if (not os.path.isdir(misc_dir)) or (not os.access(misc_dir, os.X_OK)):
			return []
		misc_files = []
		for root, dirs, files in os.walk(misc_dir):
			misc_files.extend([os.path.join(root, e) for e in files])
		return [MiscConfigFile(os.path.join(misc_dir, f), self.log) for f in misc_files]


	def __get_config_filename(self, config_file):
		"""Search for the configuration file.
		"""
		import types
		if config_file is None:
			# no config file was specified - we will look for it in the ususal locations
			conf_file_list = [os.path.expanduser(f)
				for f in CONF_LOCATIONS
				if os.path.exists(os.path.expanduser(f))]
			if not conf_file_list:
				# no possible config file found in the usual locations
				raise CBConfigUnavailableError()
			config_file = conf_file_list[0]
		else:
			# a config file was specified (e.g. via command line)
			if type(config_file) != types.StringType:
				raise CBConfigUnavailableError(
						"invalid config file specified: %s" % config_file)
			if not os.path.exists(config_file):
				raise CBConfigUnavailableError(
						"could not find the specified configuration file (%s)" % config_file)
		return config_file


	def __configure_log_handler(self):
		"""Configure the log handler of the CryptoBox according to the config.
		"""
		log_level = self.prefs["Log"]["Level"].upper()
		log_level_avail = ["DEBUG", "INFO", "WARN", "ERROR"]
		if not log_level in log_level_avail:
			raise CBConfigInvalidValueError("Log", "Level", log_level,
					"invalid log level: only %s are allowed" % str(log_level_avail))
		log_destination = self.prefs["Log"]["Destination"].lower()
		## keep this in sync with the spec and the log_destination branches below
		log_dest_avail = ['file', 'syslog']
		if not log_destination in log_dest_avail:
			raise CBConfigInvalidValueError("Log", "Destination", log_destination,
					"invalid log destination: only %s are allowed" % str(log_dest_avail))
		if log_destination == 'file':
			try:
				log_handler = logging.FileHandler(self.prefs["Log"]["Details"])
			except IOError:
				raise CBEnvironmentError("could not write to log file (%s)" % \
						self.prefs["Log"]["Details"])
			log_handler.setFormatter(
					logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
		elif log_destination == 'syslog':
			log_facility = self.prefs["Log"]["Details"].upper()
			log_facil_avail = ['KERN', 'USER', 'MAIL', 'DAEMON', 'AUTH', 'SYSLOG',
					'LPR', 'NEWS', 'UUCP', 'CRON', 'AUTHPRIV', 'LOCAL0', 'LOCAL1',
					'LOCAL2', 'LOCAL3', 'LOCAL4', 'LOCAL5', 'LOCAL6', 'LOCAL7']
			if not log_facility in log_facil_avail:
				raise CBConfigInvalidValueError("Log", "Details", log_facility,
						"invalid log details for 'syslog': only %s are allowed" % \
						str(log_facil_avail))
			## retrive the log priority from the syslog module
			log_handler = LocalSysLogHandler("CryptoBox",
					getattr(syslog, 'LOG_%s' % log_facility))
			log_handler.setFormatter(
					logging.Formatter('%(asctime)s CryptoBox %(levelname)s: %(message)s'))
		else:
			## this should never happen - we just have it in case someone forgets
			## to update the spec, the 'log_dest_avail' or the above branches
			raise CBConfigInvalidValueError("Log", "Destination", log_destination,
					"invalid log destination: only %s are allowed" % str(log_dest_avail))
		cbox_log = logging.getLogger("CryptoBox")
		## remove previous handlers (from 'basicConfig')
		cbox_log.handlers = []
		## add new one
		cbox_log.addHandler(log_handler)
		## do not call parent's handlers
		cbox_log.propagate = False
		## 'log_level' is a string -> use 'getattr'
		cbox_log.setLevel(getattr(logging, log_level))
		## the logger named "CryptoBox" is configured now


	validation_spec = """
[Main]
AllowedDevices = list(min=1)
DefaultVolumePrefix = string(min=1)
DefaultCipher = string(default="aes-cbc-essiv:sha256")
ConfigVolumeLabel = string(min=1, default="cbox_config")
UseConfigPartition = integer(min=0, max=1, default=0)
DisabledPlugins = list(default=list())

[Locations]
MountParentDir = directoryExists(default="/var/cache/cryptobox-server/mnt")
SettingsDir = directoryExists(default="/var/cache/cryptobox-server/settings")
TemplateDir = directoryExists(default="/usr/share/cryptobox-server/template")
DocDir = directoryExists(default="/usr/share/doc/cryptobox-server/www-data")
PluginDir = listOfExistingDirectories(default=list("/usr/share/cryptobox-server/plugins"))
EventDir = string(default="/etc/cryptobox-server/events.d")

[Log]
Level = option("debug", "info", "warn", "error", default="warn")
Destination = option("file", "syslog", default="file")
Details = string(min=1, default="/var/log/cryptobox-server/cryptobox.log")

[WebSettings]
Stylesheet = string(min=1)
Languages = list(min=1,default=list("en"))

[Programs]
cryptsetup = fileExecutable(default="/sbin/cryptsetup")
mkfs = fileExecutable(default="/sbin/mkfs")
nice = fileExecutable(default="/usr/bin/nice")
blkid = fileExecutable(default="/sbin/blkid")
blockdev = fileExecutable(default="/sbin/blockdev")
mount = fileExecutable(default="/bin/mount")
umount = fileExecutable(default="/bin/umount")
super = fileExecutable(default="/usr/bin/super")
# this is the "program" name as defined in /etc/super.tab
CryptoBoxRootActions = string(min=1)

[PluginSettings]
[[__many__]]
		"""

	pluginValidationSpec = """
[__many__]
visibility = boolean(default=None)
requestAuth = boolean(default=None)
rank = integer(default=None)
		"""
	
	userDatabaseSpec = """
[admins]
admin = string(default=d033e22ae348aeb5660fc2140aec35850c4da997)
		"""
	

class CryptoBoxSettingsValidator(validate.Validator):
	"""Some custom configuration check functions.
	"""

	def __init__(self):
		validate.Validator.__init__(self)
		self.functions["directoryExists"] = self.check_directory_exists
		self.functions["fileExecutable"] = self.check_file_executable
		self.functions["fileWriteable"] = self.check_file_writeable
		self.functions["listOfExistingDirectories"] = self.check_existing_directories
	

	def check_directory_exists(self, value):
		"""Is the directory accessible?
		"""
		dir_path = os.path.abspath(value)
		if not os.path.isdir(dir_path):
			raise validate.VdtValueError("%s (not found)" % value)
		if not os.access(dir_path, os.X_OK):
			raise validate.VdtValueError("%s (access denied)" % value)
		return dir_path
	

	def check_file_executable(self, value):
		"""Is the file executable?
		"""
		file_path = os.path.abspath(value)
		if not os.path.isfile(file_path):
			raise validate.VdtValueError("%s (not found)" % value)
		if not os.access(file_path, os.X_OK):
			raise validate.VdtValueError("%s (access denied)" % value)
		return file_path
	

	def check_file_writeable(self, value):
		"""Is the file writeable?
		"""
		file_path = os.path.abspath(value)
		if os.path.isfile(file_path):
			if not os.access(file_path, os.W_OK):
				raise validate.VdtValueError("%s (not found)" % value)
		else:
			parent_dir = os.path.dirname(file_path)
			if os.path.isdir(parent_dir) and os.access(parent_dir, os.W_OK):
				return file_path
			raise validate.VdtValueError("%s (directory does not exist)" % value)
		return file_path


	def check_existing_directories(self, value):
		"""Are these directories accessible?
		"""
		if not value:
			raise validate.VdtValueError("no plugin directory specified")
		if not isinstance(value, list):
			value = [value]
		result = []
		for one_dir in value:
			dir_path = os.path.abspath(one_dir)
			if not os.path.isdir(dir_path):
				raise validate.VdtValueError(
						"%s (plugin directory not found)" % one_dir)
			if not os.access(dir_path, os.X_OK):
				raise validate.VdtValueError(
						"%s (access denied for plugin directory)" % one_dir)
			result.append(dir_path)
		return result


class MiscConfigFile:
	"""all other config files (e.g. a ssl certificate) to be stored"""

	maxSize = 20480

	def __init__(self, filename, logger):
		self.filename = filename
		self.log = logger
		self.content = None
		self.load()

	
	def load(self):
		"""Load a configuration file into memory.
		"""
		fdesc = open(self.filename, "rb")
		## limit the maximum size
		self.content = fdesc.read(self.maxSize)
		if fdesc.tell() == self.maxSize:
			self.log.warn("file in misc settings directory (" + str(self.filename) \
					+ ") is bigger than allowed (" + str(self.maxSize) + ")")
		fdesc.close()


	def save(self):
		"""Save a configuration file to disk.
		"""
		## overriding of ro-files is not necessary (e.g. samba-include.conf)
		if os.path.exists(self.filename) and not os.access(self.filename, os.W_OK):
			return True
		save_dir = os.path.dirname(self.filename)
		## create the directory, if necessary
		if not os.path.isdir(save_dir):
			try:
				os.mkdir(save_dir)
			except IOError:
				return False
		## save the content of the file
		try:
			fdesc = open(self.filename, "wb")
		except IOError:
			return False
		try:
			fdesc.write(self.content)
			fdesc.close()
			return True
		except IOError:
			fdesc.close()
			return False



class LocalSysLogHandler(logging.Handler):
	"""Pass logging messages to a local syslog server without unix sockets.

	derived from: logging.SysLogHandler
	"""

	def __init__(self, prepend='CryptoBox', facility=syslog.LOG_USER):
		logging.Handler.__init__(self)
		self.formatter = None
		self.facility = facility
		syslog.openlog(prepend, 0, facility)
	

	def close(self):
		"""close the syslog connection
		"""
		syslog.closelog()
		logging.Handler.close(self)


	def emit(self, record):
		"""format and send the log message
		"""
		msg = "%s: %s" % (record.levelname, record.getMessage())
		try:
			syslog.syslog(record.levelno, msg)
		except Exception:
			self.handleError(record)

