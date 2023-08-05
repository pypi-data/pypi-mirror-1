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

"""Some useful functions for the CryptoBox.
"""

__revision__ = "$Id"

import logging
import os
import re

LOGGER = logging.getLogger("CryptoBox")


def get_available_partitions():
	"retrieve a list of all available containers"
	ret_list = []
	try:
		## the following reads all lines of /proc/partitions and adds the mentioned devices
		fpart = open("/proc/partitions", "r")
		try:
			line = fpart.readline()
			while line:
				p_details = line.split()
				if (len(p_details) == 4):
					## the following code prevents double entries like /dev/hda and /dev/hda1
					(p_major, p_minor, p_size, p_device) = p_details
					## ignore lines with: invalid minor/major or extend partitions (size=1)
					if  re.search('^[0-9]*$', p_major) and \
							re.search('^[0-9]*$', p_minor) and (p_size != "1"):
						## for some parent devices we have to remove a 'p' (partition)
						## an example are partitionable mdadm raid devices (e.g. md1p1)
						p_parent = re.sub('p?[1-9]?[0-9]$', '', p_device)
						if p_parent == p_device:
							if [e for e in ret_list
									if re.search('^' + p_parent + 'p?[1-9]?[0-9]$', e)]:
								## major partition - its children are already in the list
								pass
							else:
								## major partition - but there are no children for now
								ret_list.append(p_device)
						else:
							## minor partition - remove parent if necessary
							if p_parent in ret_list:
								ret_list.remove(p_parent)
							ret_list.append(p_device)
				line = fpart.readline()
		finally:
			fpart.close()
		return [ get_absolute_devicename(e) for e in ret_list ]
	except IOError:
		LOGGER.warning("Could not read /proc/partitions")
		return []


def get_absolute_devicename(shortname):
	"""	returns the absolute file name of a device (e.g.: "hda1" -> "/dev/hda1")
		this does also work for device mapper devices
		if the result is non-unique, one arbitrary value is returned
	"""
	if re.search('^/', shortname):
		return shortname
	default = os.path.join("/dev", shortname)
	if os.path.exists(default):
		return default
	result = find_major_minor_of_device(shortname)
	## if no valid major/minor was found -> exit
	if not result:
		return default
	(major, minor) = result
	## for device-mapper devices (major == 254) ...
	if major == 254:
		result = find_major_minor_device("/dev/mapper", major, minor)
		if result:
			return result[0]
	## now check all files in /dev
	result = find_major_minor_device("/dev", major, minor)
	if result:
		return result[0]
	return default


def find_major_minor_of_device(device):
	"""Return the major/minor numbers of a block device.
	"""
	if re.match("/", device) or \
			not os.path.exists(os.path.join(os.path.sep, "sys", "block", device)):
		## maybe it is an absolute device name
		if not os.path.exists(device):
			return None
		## okay - it seems to to a device node
		rdev = os.stat(device).st_rdev
		return (os.major(rdev), os.minor(rdev))
	blockdev_info_file = os.path.join(os.path.join(
			os.path.sep,"sys","block", device), "dev")
	try:
		f_blockdev_info = open(blockdev_info_file, "r")
		blockdev_info = f_blockdev_info.read()
		f_blockdev_info.close()
		(str_major, str_minor) = blockdev_info.split(":")
		## numeric conversion
		try:
			major = int(str_major)
			minor = int(str_minor)
			return (major, minor)
		except ValueError:
			## unknown device numbers -> stop guessing
			return None
	except IOError:
		pass
		return None


def find_major_minor_device(dirpath, major, minor):
	"""Returns the names of devices with the specified major and minor number.
	"""
	collected = []
	try:
		subdirs = [os.path.join(dirpath, e) for e in os.listdir(dirpath)
				if (not os.path.islink(os.path.join(dirpath, e))) and \
				os.path.isdir(os.path.join(dirpath, e))]
		## do a recursive call to parse the directory tree
		for dirs in subdirs:
			collected.extend(find_major_minor_device(dirs, major, minor))
		## filter all device inodes in this directory
		collected.extend([os.path.realpath(os.path.join(dirpath, e))
				for e in os.listdir(dirpath)
				if (os.major(os.stat(os.path.join(dirpath, e)).st_rdev) == major) \
				and (os.minor(os.stat(os.path.join(dirpath, e)).st_rdev) == minor)])
		## remove double entries
		result = []
		for item in collected:
			if item not in result:
				result.append(item)
		return result
	except OSError:
		return []


def get_parent_blockdevices():
	"""Return a list of all block devices that contain other devices.
	"""
	devs = []
	for line in file("/proc/partitions"):
		p_details = line.split()
		## we expect four values - otherwise continue with next iteration
		if len(p_details) != 4:
			continue
		(p_major, p_minor, p_size, p_device) = p_details
		## we expect numeric values in the first two columns
		if re.search(r'\D', p_major) or re.search(r'\D', p_minor):
			continue
		## now let us check, if it is a (parent) block device or a partition
		if not os.path.isdir(os.path.join(os.path.sep, "sys", "block", p_device)):
			continue
		devs.append(p_device)
	return [ get_absolute_devicename(e) for e in devs ]


def is_part_of_blockdevice(parent, subdevice):
	"""Check if the given block device is a parent of 'subdevice'.

	e.g. for checking if a partition belongs to a block device
	"""
	try:
		(par_major, par_minor) = find_major_minor_of_device(parent)
		(sub_major, sub_minor) = find_major_minor_of_device(subdevice)
	except TypeError:
		## at least one of these devices did not return a valid major/minor combination
		return False
	## search the entry below '/sys/block' belonging to the parent
	root = os.path.join(os.path.sep, 'sys', 'block')
	for bldev in os.listdir(root):
		blpath = os.path.join(root, bldev, 'dev')
		if os.access(blpath, os.R_OK):
			try:
				if (str(par_major), str(par_minor)) == tuple([e
						for e in file(blpath)][0].strip().split(":",1)):
					parent_path = os.path.join(root, bldev)
					break
			except (IndexError, OSError):
				pass
	else:
		## no block device with this major/minor combination found below '/sys/block'
		return False
	for subbldev in os.listdir(parent_path):
		subblpath = os.path.join(parent_path, subbldev, "dev")
		if os.access(subblpath, os.R_OK):
			try:
				if (str(sub_major), str(sub_minor)) == tuple([e
						for e in file(subblpath)][0].strip().split(":",1)):
					## the name of the subdevice node is not important - we found it!
					return True
			except (IndexError, OSError):
				pass
	return False


def get_blockdevice_size(device):
	"""Return the size of a blockdevice in megabyte.
	"""
	if not device:
		return -1
	try:
		rdev = os.stat(device).st_rdev
	except OSError:
		return -1
	minor = os.minor(rdev)
	major = os.major(rdev)
	for line in file("/proc/partitions"):
		try:
			elements = line.split()
			if len(elements) != 4:
				continue
			if (int(elements[0]) == major) and (int(elements[1]) == minor):
				return int(elements[2])/1024
		except ValueError:
			pass
	return -1


def get_blockdevice_size_humanly(device):
	"""Return a human readable size of a blockdevice.
	"""
	size = get_blockdevice_size(device)
	if size > 5120:
		return "%dGB" % int(size/1024)
	else:
		return "%dMB" % size

