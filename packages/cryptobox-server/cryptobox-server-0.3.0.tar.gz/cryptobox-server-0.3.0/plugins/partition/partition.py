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

"""The partition feature of the CryptoBox.
"""

__revision__ = "$Id"

import subprocess
import os
import re
import logging
import cryptobox.core.tools as cbox_tools
import cryptobox.plugins.base
from cryptobox.core.exceptions import *


PARTTYPES = {
	"windows"	: ["0xC", "vfat"],
	"linux"	: ["L", "ext3"]}

CONFIGPARTITION = {
	"size"	: 5,	# size of configuration partition (if necessary) in MB
	"type"	: "L",
	"fs"	: "ext2"}


class partition(cryptobox.plugins.base.CryptoBoxPlugin):
	"""The partition feature of the CryptoBox.
	"""

	plugin_capabilities = [ "system" ]
	plugin_visibility = [ "preferences" ]
	request_auth = True
	rank = 80

	def do_action(self, **args):
		"""Show the partitioning form and execute the requested action.
		"""
		## load default hdf values
		self.__prepare_dataset()
		## retrieve some values from 'args' - defaults are empty
		self.blockdevice = self.__get_selected_device(args)
		self.with_config_partition = self.__is_with_config_partition()
		self.cbox.log.debug(
				"partition plugin: selected device=%s" % str(self.blockdevice))
		self.blockdevice_size = self.__get_available_device_size(self.blockdevice)
		## no (or invalid) device was supplied
		if not self.blockdevice:
			return self.__action_select_device()
		## exit if the blockdevice is not writeable
		if not os.access(self.blockdevice, os.W_OK):
			self.hdf["Data.Warning"] = "DeviceNotWriteable"
			return self.__action_select_device()
		## no confirm setting?
		if not args.has_key("confirm") or (args["confirm"] != "1"):
			self.hdf["Data.Warning"] = "Plugins.partition.FormatNotConfirmed"
			return self.__action_select_device()
		elif args.has_key("easy"):
			return self.__action_easy_setup()
		elif args.has_key("add_part"):
			return self.__action_add_partition(args)
		elif args.has_key("finish"):
			return self.__action_finish(args)
		elif args.has_key("cancel"):
			return self.__action_select_device()
		## check if we should remove a partition
		del_args = [ e for e in args.keys() if re.match(r"del_part_[\d]+$", e) ]
		if len(del_args) == 1:
			try:
				num_part = int(del_args[0][9:])
			except ValueError:
				self.cbox.log.warn(
						"partition: invalid partition number to delete (%s)" % del_args[0])
				return self.__action_select_device()
			return self.__action_del_partition(args, num_part)
		else:	# for "select_device" and for invalid targets
			return self.__action_select_device()


	def get_status(self):
		"""The status of this plugin is the selected device and some information.
		"""
		return "%s / %s / %s" % (self.blockdevice, self.blockdevice_size,
				self.with_config_partition)


	def get_warnings(self):
		warnings = []
		## this check is done _after_ "reset_dataset" -> if there is
		## a config partition, then it was loaded before
		if self.cbox.prefs.requires_partition() \
				and not self.cbox.prefs.get_active_partition():
			warnings.append((50, "Plugins.%s.ReadOnlyConfig" % self.get_name()))
		## check required programs
		if not os.path.isfile(self.root_action.SFDISK_BIN):
			warnings.append((53, "Plugins.%s.MissingProgramSfdisk" % self.get_name()))
		if not os.path.isfile(self.root_action.MKFS_BIN):
			warnings.append((56, "Plugins.%s.MissingProgramMkfs" % self.get_name()))
		if not os.path.isfile(self.root_action.LABEL_BIN):
			warnings.append((40, "Plugins.%s.MissingProgramE2label" % self.get_name()))
		return warnings


	def __prepare_dataset(self):
		"""Set some hdf values.
		"""
		self.hdf["Data.AdditionalStylesheets.%s" % self.get_name()] = \
				os.path.join(self.plugin_dir, "partition.css")
		self.hdf[self.hdf_prefix + "PluginDir"] = self.plugin_dir


	def __get_selected_device(self, args):
		"""Check the selected device (valid, not busy, ...).
		"""
		try:
			blockdevice = args["block_device"]
		except KeyError:
			return None
		if not self.__is_device_valid(blockdevice):
			return None
		if self.__is_device_busy(blockdevice):
			self.hdf["Data.Warning"] = "Plugins.partition.DiskIsBusy"
			return None
		return blockdevice


	def __is_device_valid(self, blockdevice):
		"""Check if the device is valid and allowed.
		"""
		if not blockdevice:
			return False
		if not self.cbox.is_device_allowed(blockdevice):
			return False
		if not blockdevice in cbox_tools.get_parent_blockdevices():
			return False
		return True


	def __is_device_busy(self, blockdevice):
		"""check if the device (or one of its partitions) is mounted
		"""
		## the config partition is ignored, as it will get unmounted if necessary
		for cont in self.cbox.get_container_list():
			if cbox_tools.is_part_of_blockdevice(blockdevice, cont.get_device()) \
					and cont.is_mounted():
				return True
		return False


	def __action_select_device(self):
		"""Show a form to select the device for partitioning.
		"""
		block_devices = [e
			for e in cbox_tools.get_parent_blockdevices()
			if self.cbox.is_device_allowed(e)]
		counter = 0
		for dev in block_devices:
			self.hdf[self.hdf_prefix + "BlockDevices.%d.name" % counter] = dev
			self.hdf[self.hdf_prefix + "BlockDevices.%d.size" % counter] = \
					cbox_tools.get_blockdevice_size_humanly(dev)
			self.cbox.log.debug("found a suitable block device: %s" % dev)
			counter += 1
		if self.with_config_partition:
			self.hdf[self.hdf_prefix + "CreateConfigPartition"] = "1"
		## there is no disk available
		if not block_devices:
			self.hdf["Data.Warning"] = "Plugins.partition.NoDisksAvailable"
		return "select_device"


	def __action_add_partition(self, args):
		"""Add a selected partition to the currently proposed partition table.
		"""
		self.hdf[self.hdf_prefix + "Device"] = self.blockdevice
		self.hdf[self.hdf_prefix + "Device.Size"] = self.blockdevice_size
		parts = self.__get_partitions_from_args(args)
		self.__set_partition_data(parts)
		return "set_partitions"
	

	def __action_del_partition(self, args, part_num):
		"""Remove a partition from the proposed partition table.
		"""
		self.hdf[self.hdf_prefix + "Device"] = self.blockdevice
		self.hdf[self.hdf_prefix + "Device.Size"] = self.blockdevice_size
		parts = self.__get_partitions_from_args(args)
		## valid partition number to be deleted?
		if part_num < len(parts):
			del parts[part_num]
		self.__set_partition_data(parts)
		return "set_partitions"


	def __action_finish(self, args):
		"""Write the partition table.
		"""
		parts = self.__get_partitions_from_args(args)
		if parts:
			self.__set_partition_data(parts)
			if cbox_tools.is_part_of_blockdevice(self.blockdevice,
					self.cbox.prefs.get_active_partition()):
				self.cbox.prefs.umount_partition()
			if not self.__run_fdisk(parts):
				self.hdf["Data.Warning"] = "Plugins.partition.PartitioningFailed"
				self.cbox.log.warn(
						"partition: failed to partition device: %s" % self.blockdevice)
				return self.__action_add_partition(args)
			else:
				## tricky problem: if the device was partitioned, then a created config
				## partition is still part of the containerlist, as the label is not
				## checked again - very ugly!!! So we will call reReadContainerList
				## after formatting the last partition - see below
				#self.cbox.reread_container_list()
				format_ok = True
				counter = 0
				## initialize the generator
				format_part_gen = self.__format_partitions(parts)
				while counter < len(parts):
					## first part: get the device name
					counter += 1
					## second part: do the real formatting of a partition
					result = format_part_gen.next()
					## after the first partiton, we can reRead the containerList
					## (as the possible config partition was already created)
					if self.with_config_partition and (counter == 1):
						## important: reRead the containerList - but somehow it
						## breaks the flow (hanging process)
						#self.cbox.reReadContainerList()
						## write config data
						self.cbox.prefs.mount_partition()
						try:
							self.cbox.prefs.write()
							self.cbox.log.info("settings stored on config partition")
						except IOError:
							self.cbox.log.warn(
									"Failed to store settings on new config partition")
					## return the result
					if not result:
						format_ok = False
				if format_ok:
					self.hdf["Data.Success"] = "Plugins.partition.Partitioned"
				else:
					self.hdf["Data.Warning"] = "Plugins.partition.FormattingFailed"
				return "empty"
		else:
			return self.__action_add_partition(args)


	def __action_easy_setup(self):
		"""Do automatic partitioning (create only one big partition).
		"""
		import types
		## we do not have to take special care for a possible config partition
		parts = [ { "size": self.blockdevice_size, "type": "windows" } ]
		## umount partition if necessary
		if cbox_tools.is_part_of_blockdevice(self.blockdevice,
				self.cbox.prefs.get_active_partition()):
			self.cbox.prefs.umount_partition()
		## partition it
		if not self.__run_fdisk(parts):
			self.hdf["Data.Warning"] = "Plugins.partition.PartitioningFailed"
			return None
		## "formatPartitions" is a generator, returning device names and bolean values
		result = [e for e in self.__format_partitions(parts)
				if type(e) == types.BooleanType]
		if self.with_config_partition:
			self.cbox.prefs.mount_partition()
			if not self.cbox.prefs.write():
				self.cbox.log.warn("Failed to store settings on new config partition")
		## check if there is a "False" return value
		if False in result:
			## operation failed
			self.hdf["Data.Warning"] = "Plugins.partition.FormattingFailed"
			self.cbox.log.info("easy partitioning failed")
			return "select_partitions"
		else:
			## operation was successful
			self.hdf["Data.Success"] = "Plugins.partition.EasySetup"
			self.cbox.log.info("easy partitioning succeeded")
			## do not show the disk overview immediately
			## it does not get updated that fast
			return { "plugin":"system_preferences", "values":[] }


	def __set_partition_data(self, parts):
		"""Set some hdf values for the currently proposed partition table.
		"""
		avail_size = self.blockdevice_size
		i = 0
		for part in parts:
			self.cbox.log.debug(part)
			self.hdf[self.hdf_prefix + "Parts.%d.Size" % i] = part["size"]
			self.hdf[self.hdf_prefix + "Parts.%d.Type" % i] = part["type"]
			avail_size -= part["size"]
			i += 1
		self.hdf[self.hdf_prefix + "availSize"] = avail_size
		if self.with_config_partition:
			self.hdf[self.hdf_prefix + "CreateConfigPartition"] = "1"
		for ptype in PARTTYPES.keys():
			self.hdf[self.hdf_prefix + "Types.%s" % ptype] = ptype
		## store the currently existing partitions of the choosen block device
		current_containers = [ e for e in self.cbox.get_container_list()
				if cbox_tools.is_part_of_blockdevice(self.blockdevice, e.get_device()) ]
		for (index, cont) in enumerate(current_containers):
			self.hdf[self.hdf_prefix + "ExistingContainers.%d" % index] = \
					cont.get_device()


	def __get_partitions_from_args(self, args):
		"""Filter the given arguments and construct a partition table.
		"""
		parts = []
		done = False
		avail_size = self.blockdevice_size
		i = -1
		while not done:
			i += 1
			try:
				## skip every unconfirmed (probably the last) partition if we should not add it
				if args.has_key("part%d_unconfirmed" % i) and \
						not args.has_key("add_part"):
					continue
				size = int(args["part%d_size" % i])
				part_type = args["part%d_type" % i]
				if int(size) > avail_size:
					self.hdf["Data.Warning"] = "Plugins.partition.PartitionTooBig"
					continue
				if int(size) < 10:
					self.hdf["Data.Warning"] = "Plugins.partition.PartitionTooSmall"
					continue
				if not part_type in PARTTYPES.keys():
					continue
				parts.append({"size":size, "type":part_type})
				avail_size -= size
			except TypeError:
				pass
			except KeyError:
				done = True
		return parts


	def __get_available_device_size(self, device):
		"""calculate the available size (MB) of the device
		also consider a (possible) configuration partition
		"""
		device_size = cbox_tools.get_blockdevice_size(device)
		if device_size < 0:
			return 0
		if self.with_config_partition:
			device_size -= CONFIGPARTITION["size"]
		return device_size


	def __is_with_config_partition(self):
		"""check if we have to create a configuration partition
		"""
		if self.cbox.prefs.requires_partition():
			active = self.cbox.prefs.get_active_partition()
			## we need a partition, if there is no active one
			if not active:
				return True
			## check if the active one is part of the current device
			return cbox_tools.is_part_of_blockdevice(self.blockdevice, active)
		return False


	def __run_fdisk(self, parts):
		"""Call fdisk to partition the device.
		"""
		## check if the device is completely filled (to avoid some empty last blocks)
		avail_size = self.blockdevice_size
		for one_part in parts:
			avail_size -= one_part["size"]
		self.cbox.log.debug("remaining size: %d" % avail_size)
		is_filled = avail_size == 0
		proc = subprocess.Popen(
			shell = False,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"plugin",
				os.path.join(self.plugin_dir, "root_action.py"),
				"partition",
				self.blockdevice])
		for line in self.__get_sfdisk_layout(parts, is_filled):
			proc.stdin.write(line + "\n")
		#TODO: if running inside of an uml, then sfdisk hangs at "nanosleep({3,0})"
		# very ugly - maybe a uml bug?
		# it seems, like this can be avoided by running uml with the param "aio=2.4"
		(output, error) = proc.communicate()
		if proc.returncode != 0:
			self.cbox.log.debug("partitioning failed: %s" % error)
		return proc.returncode == 0


	def __get_sfdisk_layout(self, param_parts, is_filled):
		"""this generator returns the input lines for sfdisk
		"""
		parts = param_parts[:]
		## first a (possible) configuration partition - so it will be reusable
		if self.with_config_partition:
			## fill the main table (including a config partition)
			yield ",%d,%s" % (CONFIGPARTITION["size"], CONFIGPARTITION["type"])
		## one primary partition
		if is_filled and (len(parts) == 1):
			## fill the rest of the device
			yield ",,%s,*" % PARTTYPES[parts[0]["type"]][0]
		else:
			## only use the specified size
			yield ",%d,%s,*" % (parts[0]["size"], PARTTYPES[parts[0]["type"]][0])
		del parts[0]
		## no extended partition, if there is only one disk
		if not parts:
			return
		## an extended container for the rest
		yield ",,E"
		## an empty partition in main table
		yield ";"
		## maybe another empty partition if there is no config partition
		if not self.with_config_partition:
			yield ";"
		while parts:
			if is_filled and (len(parts) == 1):
				yield ",,%s" % (PARTTYPES[parts[0]["type"]][0],)
			else:
				yield ",%d,%s" % (parts[0]["size"], PARTTYPES[parts[0]["type"]][0])
			del parts[0]


	def __format_partitions(self, param_parts):
		"""Format all partitions of the device.
		"""
		parts = param_parts[:]
		part_num = 1
		## maybe a config partition?
		if self.with_config_partition:
			dev_name = self.__get_partition_name(self.blockdevice, part_num)
			self.cbox.log.info("formatting config partition (%s)" % dev_name)
			if self.__format_one_partition(dev_name, CONFIGPARTITION["fs"]):
				self.__set_label_of_partition(dev_name,
						self.cbox.prefs["Main"]["ConfigVolumeLabel"])
			part_num += 1
		## the first data partition
		dev_name = self.__get_partition_name(self.blockdevice, part_num)
		part_type = PARTTYPES[parts[0]["type"]][1]
		self.cbox.log.info("formatting partition (%s) as '%s'" % (dev_name, part_type))
		yield self.__format_one_partition(dev_name, part_type)
		del parts[0]
		## other data partitions
		part_num = 5
		while parts:
			dev_name = self.__get_partition_name(self.blockdevice, part_num)
			part_type = PARTTYPES[parts[0]["type"]][1]
			self.cbox.log.info("formatting partition (%s) as '%s'" % \
					(dev_name, part_type))
			yield self.__format_one_partition(dev_name, part_type)
			part_num += 1
			del parts[0]
		return
	

	def __get_partition_name(self, blockdev, number):
		"""Return the name of a specific partition of a device

		"""
		## do we need to put a "p" between name and number?
		## TODO: should we check for existence?
		if re.search("[0-9]$", blockdev):
			## blockdev endswith a digit - we need a 'p'
			return "%sp%d" % (blockdev, number)
		else:
			## no 'p' necessary
			return "%s%d" % (blockdev, number)



	def __format_one_partition(self, dev_name, fs_type):
		"""Format a single partition
		"""
		import cryptobox.core.container
		## first: retrieve UUID - it can be removed from the database afterwards
		prev_name = [e.get_name() for e in self.cbox.get_container_list()
				if e.get_device() == dev_name]
		## call "mkfs"
		try:
			cont = cryptobox.core.container.CryptoBoxContainer(dev_name, self.cbox)
			cont.create(cryptobox.core.container.CONTAINERTYPES["plain"], fs_type=fs_type)
		except (CBInvalidType, CBCreateError, CBVolumeIsActive), err_msg:
			self.cbox.log.warn(err_msg)
			return False
		## remove unused volume entry
		if prev_name:
			del self.cbox.prefs.volumes_db[prev_name[0]]
		return True


	def __set_label_of_partition(self, dev_name, label):
		"""Set the label of a partition - useful for the config partition.
		"""
		proc = subprocess.Popen(
			shell = False,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"plugin",
				os.path.join(self.plugin_dir, "root_action.py"),
				"label",
				dev_name,
				label])
		(output, error) = proc.communicate()
		if proc.returncode == 0:
			return True
		else:
			self.cbox.log.warn("failed to create filesystem on %s: %s" % (dev_name, error))
			return False

