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

"""
this module contains some useful tools to be used during the tests

just inherit one of its classes and add some test functions
"""

__revision__ = "$Id"

TEST_DEVICE_LIST = ["ubdb", "loop", "ubda", "udbc", "ubdd", "sd"]


import os
import subprocess

def find_test_device():
	"""Search for a valid test device - the data will get lost ...

	the result is the parent blockdevice (containing the partition table)
	and the single partition
	"""
	for dev in TEST_DEVICE_LIST:
		if os.path.exists("/dev/%s" % dev) \
				and os.access("/dev/%s" % dev, os.W_OK):
			try:
				## try if it is a symlink
				return os.readlink("/dev/%s" % dev)
			except OSError:
				## not a symlink (usual)
				return "/dev/%s" % dev
	else:
		raise Exception, "no valid device for testing found"
	

def is_config_partition(device):
	"""Check if the device is a configuration partition.
	"""
	proc = subprocess.Popen(
		shell = False,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		args = [ '/sbin/e2label',
			device ])
	(stdout, stderr) = proc.communicate()
	return stdout.strip() == "cbox_config"


def umount(device):
	"""Umount the specified device if possible - ignore errors
	"""
	proc = subprocess.Popen(
		shell = False,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		args = [ '/bin/umount', '-d', device ])
	proc.wait()


def prepare_partition(blockdevice):
	"""Prepare the expected partition in the device (destroy all data)
	
	Check if 'device' is a vfat partition - if not, then
	partition 'blockdevice' and format 'device' as vfat
	"""
	if (get_fs_type(blockdevice + "1") == "vfat") \
			and (get_fs_type(blockdevice + "2") == "ext3") \
			and (get_fs_type(blockdevice + "3") is None) \
			and (get_fs_type(blockdevice + "5") is None):
		## everything is fine
		return
	else:
		## repartitioning
		proc = subprocess.Popen(
			shell = False,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [ '/sbin/sfdisk', blockdevice ])
		proc.stdin.write(",50,0xC\n,50,L\n")
		(output, error) = proc.communicate()
		if proc.returncode != 0:
			raise Exception, "could not partition the device (%s): %s" \
					% (blockdevice, output.strip())
		## formatting
		format_device(blockdevice + "1", "vfat")
		format_device(blockdevice + "2", "ext3")


def get_fs_type(device):
	proc = subprocess.Popen(
		shell = False,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		args = [ '/sbin/blkid',
			'-c', os.path.devnull,
			'-w', os.path.devnull,
			'-o', 'value',
			'-s', 'TYPE',
			device])
	(output, error) = proc.communicate()
	if (proc.returncode == 0) and output.strip():
		## everything is fine
		return output.strip()
	else:
		return None


def format_device(device, fs_type="vfat"):
		proc = subprocess.Popen(
			shell = False,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [ '/sbin/mkfs',
				'-t', fs_type,
				device ])
		(output, error) = proc.communicate()
		if proc.returncode != 0:
			raise OSError, "could not format the device (%s): %s" \
					% (device, output.strip())
	

