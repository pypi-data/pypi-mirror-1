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

'''
This is the web interface for a fileserver managing encrypted filesystems.
'''

__revision__ = "$Id"

import sys
import cryptobox.core.container as cbxContainer
from cryptobox.core.exceptions import CBEnvironmentError, CBConfigUndefinedError
import re
import os
import cryptobox.core.tools as cbxTools
import subprocess
import threading


class CryptoBox:
	'''this class rules them all!

	put things like logging, conf and other stuff in here,
	that might be used by more classes, it will be passed on to them'''


	def __init__(self, config_file=None):
		import cryptobox.core.settings as cbxSettings
		self.log = self.__get_startup_logger()
		self.prefs = cbxSettings.CryptoBoxSettings(config_file)
		self.__run_tests()
		self.__containers = []
		self.__busy_devices = {}
		self.__busy_devices_sema = threading.BoundedSemaphore()
		self.reread_container_list()


	def setup(self):
		"""Initialize the cryptobox.
		"""
		self.log.info("Starting up the CryptoBox ...")


	def cleanup(self):
		"""Umount all containers and shutdown everything safely.
		"""
		self.log.info("Shutting down the CryptoBox ...")
		## umount all containers
		self.log.info("Umounting all volumes ...")
		self.reread_container_list()
		for cont in self.get_container_list():
			if cont.is_mounted():
				cont.umount()
		## save all settings
		self.log.info("Storing local settings ...")
		## problems with storing are logged automatically
		self.prefs.write()
		# TODO: improve the configuration partition handling
		self.prefs.umount_partition()
		## shutdown logging as the last step
		try:
			self.log.info("Turning off logging ...")
			self.log.close()
		except AttributeError:
			## there should be 'close' action - but it may fail silently
			pass


	def __get_startup_logger(self):	
		"""Initialize the configured logging facility of the CryptoBox.
		
		use it with: 'self.log.[debug|info|warning|error|critical](logmessage)'
		all classes should get the logging instance during __init__:
			self.log = logging.getLogger("CryptoBox")

		first we output all warnings/errors to stderr
		as soon as we opened the config file successfully, we redirect debug output
		to the configured destination
		"""
		import logging
		## basicConfig(...) needs python >= 2.4
		try:
			log_handler = logging.getLogger("CryptoBox")
			logging.basicConfig(
					format = '%(asctime)s CryptoBox %(levelname)s: %(message)s',
					stderr = sys.stderr)
			log_handler.setLevel(logging.ERROR)
			log_handler.info("loggingsystem is up'n running")
			## from now on everything can be logged via self.log...
		except:
			raise CBEnvironmentError("couldn't initialise the loggingsystem. I give up.")
		return log_handler


	def __run_tests(self):
		"""Do some initial tests.
		"""
		self.__run_test_root_priv()

	
	def __run_test_root_priv(self):
		"""Try to run 'super' with 'CryptoBoxRootActions'.
		"""
		try:
			devnull = open(os.devnull, "w")
		except IOError:
			raise CBEnvironmentError("could not open %s for writing!" % os.devnull)
		try:
			prog_super = self.prefs["Programs"]["super"]
		except KeyError:
			raise CBConfigUndefinedError("Programs", "super")
		try:
			prog_rootactions = self.prefs["Programs"]["CryptoBoxRootActions"]
		except KeyError:
			raise CBConfigUndefinedError("Programs", "CryptoBoxRootActions")
		try:
			proc = subprocess.Popen(
				shell = False,
				stdout = devnull,
				stderr = devnull,
				args = [prog_super, prog_rootactions, "check"])
		except OSError:
			raise CBEnvironmentError(
					"failed to execute 'super' (%s)" % self.prefs["Programs"]["super"])
		proc.wait()
		if proc.returncode != 0:
			raise CBEnvironmentError("failed to call CryptoBoxRootActions ("
					+ prog_rootactions + ") via 'super' - maybe you did not add the "
					+ "appropriate line to '/etc/super.tab'?")


	def reread_container_list(self):
		"""Reinitialize the list of available containers.

		This should be called whenever the available containers may have changed.
		E.g.: after partitioning and after device addition/removal
		"""
		self.log.debug("rereading container list")
		self.__containers = []
		for device in cbxTools.get_available_partitions():
			if self.is_device_allowed(device) and not self.is_config_partition(device):
				self.__containers.append(cbxContainer.CryptoBoxContainer(device, self))
		## sort by container name
		self.__containers.sort(cmp = lambda x, y: x.get_name() < y.get_name() and -1 or 1)
	

	def get_device_busy_state(self, device):
		"""Return whether a device is currently marked as busy or not.

		The busy flag can be turned off manually (recommended) or the timeout
		can expire.
		"""
		import time
		self.__busy_devices_sema.acquire()
		## not marked as busy
		if not self.__busy_devices.has_key(device):
			self.__busy_devices_sema.release()
			return False
		## timer is expired
		if time.time() > self.__busy_devices[device]:
			del self.__busy_devices[device]
			self.__busy_devices_sema.release()
			return False
		self.__busy_devices_sema.release()
		return True


	def set_device_busy_state(self, device, new_state, timeout=300):
		"""Mark a device as busy.

		This is especially useful during formatting, as this may take a long time.
		"""
		import time
		self.__busy_devices_sema.acquire()
		self.log.debug("Turn busy flag %s: %s" % (new_state and "on" or "off", device))
		if new_state:
			self.__busy_devices[device] = time.time() + timeout
		else:
			if self.__busy_devices.has_key(device):
				del self.__busy_devices[device]
		self.log.debug("Current busy flags: %s" % str(self.__busy_devices))
		self.__busy_devices_sema.release()


	def is_config_partition(self, device):
		"""Check if a given partition contains configuration informations.

		The check is done by comparing the label of the filesystem with a string.
		"""
		proc = subprocess.Popen(
			shell = False,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.prefs["Programs"]["blkid"],
				"-c", os.path.devnull,
				"-o", "value",
				"-s", "LABEL",
				device])
		(output, error) = proc.communicate()
		return output.strip() == self.prefs["Main"]["ConfigVolumeLabel"]


	def is_device_allowed(self, devicename):
		"""check if a device is white-listed for being used as cryptobox containers
		
		also check, if the device is readable and writeable for the current user
		"""
		import types
		devicename = os.path.abspath(devicename)
		if not os.access(devicename, os.R_OK):
			self.log.debug("Skipping device without read permissions: %s" % devicename)
			return False
		if not os.access(devicename, os.W_OK):
			self.log.debug("Skipping device without write permissions: %s" % devicename)
			return False
		allowed = self.prefs["Main"]["AllowedDevices"]
		if type(allowed) == types.StringType:
			allowed = [allowed]
		for a_dev in allowed:
			if not a_dev:
				continue
			## double dots are not allowed (e.g. /dev/ide/../sda)
			if re.search("/\.\./", devicename):
				continue
			## it is not possible to check for 'realpath' - that does not work
			## for the cryptobox as /dev/ is bind-mounted (real hda-name is /opt/...)
			if re.search('^%s' % a_dev, devicename):
				self.log.debug("Adding valid device: %s" % devicename)
				return True
		self.log.debug("Skipping device not listed in Main->AllowedDevices: %s" \
				% devicename)
		return False


	def get_container_list(self, filter_type=None, filter_name=None):
		"retrieve the list of all containers of this cryptobox"
		try:
			result = self.__containers[:]
			if filter_type != None:
				if filter_type in range(len(cbxContainer.CONTAINERTYPES)):
					return [e for e in self.__containers if e.get_type() == filter_type]
				else:
					self.log.info("invalid filter_type (%d)" % filter_type)
					result.clear()
			if filter_name != None:
				result = [e for e in self.__containers if e.get_name() == filter_name]
			return result
		except AttributeError:
			return []


	def get_container(self, device):
		"retrieve the container element for this device"
		all = [e for e in self.get_container_list() if e.device == device]
		if all:
			return all[0]
		else:
			return None


	def send_event_notification(self, event, event_infos):
		"""call all available scripts in the event directory with some event information"""
		event_dir = self.prefs["Locations"]["EventDir"]
		for fname in os.listdir(event_dir):
			real_fname = os.path.join(event_dir, fname)
			if os.path.isfile(real_fname) and os.access(real_fname, os.X_OK):
				cmd_args = [ self.prefs["Programs"]["super"],
					self.prefs["Programs"]["CryptoBoxRootActions"],
					"event", real_fname, event]
				cmd_args.extend(event_infos)
				proc = subprocess.Popen(
					shell = False,
					stdout = subprocess.PIPE,
					stderr = subprocess.PIPE,
					args = cmd_args)
				(stdout, stderr) = proc.communicate()
				if proc.returncode != 0:
					self.log.warn(
							"an event script (%s) failed (exitcode=%d) to handle an event (%s): %s" % 
							(real_fname, proc.returncode, event, stderr.strip()))
				else:
					self.log.info("event handler (%s) finished successfully: %s" %
							(real_fname, event))


if __name__ == "__main__":
	CryptoBox()

