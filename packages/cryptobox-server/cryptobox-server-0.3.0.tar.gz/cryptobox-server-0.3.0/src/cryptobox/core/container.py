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

"""Manage a single container of the CryptoBox
"""

__revision__ = "$Id"

import subprocess
import os
import re
import time
from cryptobox.core.exceptions import *


CONTAINERTYPES = {
	"unused":0,
	"plain":1,
	"luks":2,
	"swap":3,
	}

FSTYPES = {
	"plain":["ext3", "ext2", "vfat", "reiserfs"],
	"swap":["swap"]}


## we use this marker to make sure, that we do not remove a non-cryptobox directory
## below the mount directory
MOUNT_DIR_MARKER = '_cryptobox_mount_dir_'


class CryptoBoxContainer:
	"""Manage a container of the CryptoBox
	"""

	__dmDir = "/dev/mapper"


	def __init__(self, device, cbox):
		self.device = device
		self.cbox = cbox
		self.uuid = None
		self.name = None
		self.cont_type = None
		self.mount = None
		self.umount = None
		self.attributes = None
		self.reset_object()


	def get_name(self):
		"""Return a humanly readable name for the container.

		Available since: 0.3.0
		"""
		return self.name


	def __set_attributes(self):
		"""Define the default attributes of a container.

		At least there should be a uuid.
		Other attributes may be added by features (e.g. automount).
		Available since: 0.3.0
		"""
		try:
			## is there already an entry in the database?
			self.attributes = self.cbox.prefs.volumes_db[self.get_name()]
			self.attributes["uuid"] = self.uuid
		except KeyError:
			## set default values
			self.attributes = { "uuid": self.uuid }
			self.cbox.prefs.volumes_db[self.get_name()] = self.attributes


	def set_name(self, new_name):
		"""Define a humanly readable name of this container.

		this also manages the name database
		Available since: 0.3.0
		"""
		old_name = self.get_name()
		if new_name == self.name:
			return
		## renaming is not possible, if the volume is active, as the mountpoint name
		## is the same as the volume name
		if self.is_mounted():
			raise CBVolumeIsActive("the container must not be active during renaming")
		if not re.search(r'^[a-zA-Z0-9_\.\- ]+$', new_name):
			raise CBInvalidName("the supplied new name contains illegal characters")
		## check for another partition with the same name
		if self.cbox.get_container_list(filter_name=new_name):
			raise CBNameIsInUse("the supplied new name is already in use for anonther partition")
		## maybe there a is an entry in the volumes database (but the partition is not active)
		try:
			## remove possibly existing inactive database item
			del self.cbox.prefs.volumes_db[new_name]
		except KeyError:
			## no entry - so nothing happens
			pass
		## set new name
		self.name = new_name
		## remove old database entry
		try:
			del self.cbox.prefs.volumes_db[old_name]
		except KeyError:
			pass
		## set new volumes database entry
		self.cbox.prefs.volumes_db[new_name] = self.attributes
		try:
			self.cbox.prefs.volumes_db.write()
		except IOError:
			self.cbox.log.warn("Failed to store volumes database after set_name")


	def is_writeable(self):
		"""Return if the container is writeable

		this only affects actions like formatting or partitioning
		write access for the mounted content is not considered
		Available since: 0.3.3
		"""
		## symlinks are followed automatically
		return os.access(self.get_device(), os.W_OK)


	def get_device(self):
		"""Return the device name of the container

		e.g.: /dev/hdc1
		Available since: 0.3.0
		"""
		return self.device


	def get_type(self):
		"""Return the type (int) of this container.

		Available since: 0.3.0
		"""
		return self.cont_type


	def is_mounted(self):
		"""Check if the container is currently mounted.

		Available since: 0.3.0
		"""
		return os.path.ismount(self.__get_mount_point())
	

	def get_capacity(self):
		"""Return the current capacity state of the volume.

		the volume may not be mounted
		the result is a tuple of values in megabyte:
			(size, available, used)
		Available since: 0.3.0
		"""
		info = os.statvfs(self.__get_mount_point())
		return (
			int(info.f_bsize*info.f_blocks/1024/1024),
			int(info.f_bsize*info.f_bavail/1024/1024),
			int(info.f_bsize*(info.f_blocks-info.f_bavail)/1024/1024))
	

	def get_size(self):
		"""return the size of the block device (_not_ of the filesystem)

		the result is a value in megabyte
		an error is indicated by "-1"
		Available since: 0.3.0
		"""
		import cryptobox.core.tools as cbxtools
		return cbxtools.get_blockdevice_size(self.device)


	def reset_object(self):
		"""	recheck the information about this container

		this is especially useful after changing the type via 'create'
		Available since: 0.3.0
		"""
		self.uuid = self.__get_uuid()
		self.cont_type = self.__get_type_of_partition()
		self.name = self.__get_name_of_container()
		self.__set_attributes()
		if self.cont_type == CONTAINERTYPES["luks"]:
			self.mount = self.__mount_luks
			self.umount = self.__umount_luks
		elif self.cont_type == CONTAINERTYPES["plain"]:
			self.mount = self.__mount_plain
			self.umount = self.__umount_plain


	def create(self, cont_type, password=None, fs_type="ext3"):
		"""Format a container.

		Also set a password for encrypted container.
		Available since: 0.3.0
		"""
		if not fs_type in FSTYPES["plain"]:
			raise CBInvalidType("invalid filesystem type supplied: %s" % str(fs_type))
		old_name = self.get_name()
		if cont_type == CONTAINERTYPES["luks"]:
			self.__create_luks(password, fs_type)
		elif cont_type == CONTAINERTYPES["plain"]:
			self.__create_plain(fs_type)
		else:
			raise CBInvalidType("invalid container type (%d) supplied" % (cont_type, ))
		## no exception was raised during creation -> we can continue
		## reset the properties (encryption state, ...) of the device
		self.reset_object()
		## restore the old name (must be after reset_object)
		try:
			self.set_name(old_name)
		except CBNameIsInUse:
			## failure is okay
			pass
	

	def change_password(self, oldpw, newpw):
		"""Change the password of an encrypted container.

		Raises an exception for plaintext container.
		Available since: 0.3.0
		"""
		if self.cont_type != CONTAINERTYPES["luks"]:
			raise CBInvalidType("changing of password is possible only for luks containers")
		if not oldpw:
			raise CBInvalidPassword("no old password supplied for password change")
		if not newpw:
			raise CBInvalidPassword("no new password supplied for password change")
		## return if new and old passwords are the same
		if oldpw == newpw:
			return
		if self.is_mounted():
			raise CBVolumeIsActive("this container is currently active")
		## remove any potential open luks mapping
		self.__umount_luks()
		## create the luks header
		proc = subprocess.Popen(
			shell = False,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"cryptsetup",
				"luksAddKey",
				self.device,
				"--batch-mode"])
		proc.stdin.write("%s\n%s" % (oldpw, newpw))
		(output, errout) = proc.communicate()
		if proc.returncode != 0:
			error_msg = "Could not add a new luks key: %s - %s" \
					% (output.strip(), errout.strip(), )
			self.cbox.log.error(error_msg)
			raise CBChangePasswordError(error_msg)
		## retrieve the key slot we used for unlocking
		keys_found = re.search(r'key slot (\d{1,3}) unlocked', output).groups()
		if keys_found:
			keyslot = int(keys_found[0])
		else:
			raise CBChangePasswordError("could not get the old key slot")
		## remove the old key
		proc = subprocess.Popen(
			shell = False,
			stdin = None,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["cryptsetup"],
				"--batch-mode",
				"luksDelKey",
				self.device,
				"%d" % (keyslot, )])
		proc.wait()
		if proc.returncode != 0:
			error_msg = "Could not remove the old luks key: %s" % (proc.stderr.read().strip(), )
			self.cbox.log.error(error_msg)
			raise CBChangePasswordError(error_msg)
		

	def is_busy(self):
		"""Return the current state of the busy flag of this device.

		The busy flag is mainly used to indicate that the device may not be used
		while it is being formatted or similar.
		Available since: 0.3.1
		"""
		return self.cbox.get_device_busy_state(self.device)


	def set_busy(self, new_state, timeout=300):
		"""Set the busy state of this device.

		Either set or remove this flag.
		The timeout is optional and defaults to five minutes.
		Available since: 0.3.1
		"""
		self.cbox.set_device_busy_state(self.device, new_state, timeout)


	## ****************** internal stuff *********************

	def __get_name_of_container(self):
		"""retrieve the name of the container by querying the database
		call this function only for the initial setup of the container object"""
		found_name = None
		for key in self.cbox.prefs.volumes_db.keys():
			if self.cbox.prefs.volumes_db[key]["uuid"] == self.uuid:
				found_name = key
		if found_name:
			return found_name
		## there is no name defined for this uuid - we will propose a good one
		prefix = self.cbox.prefs["Main"]["DefaultVolumePrefix"]
		unused_found = False
		counter = 1
		while not unused_found:
			guess = prefix + str(counter)
			if self.cbox.prefs.volumes_db.has_key(guess):
				counter += 1
			else:
				unused_found = True
		return guess


	def __get_uuid(self):
		"""Retrieve the uuid of the container device.
		"""
		if self.__get_type_of_partition() == CONTAINERTYPES["luks"]:
			guess = self.__get_luks_uuid()
		else:
			guess = self.__get_non_luks_uuid()
		## did we get a valid value?
		if guess:
			return guess
		else:
			## emergency default value
			return self.device.replace(os.path.sep, "_")


	def __get_luks_uuid(self):
		"""get uuid for luks devices"""
		proc = subprocess.Popen(
			shell = False,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [self.cbox.prefs["Programs"]["cryptsetup"],
				"luksUUID",
				self.device])
		(stdout, stderr) = proc.communicate()
		if proc.returncode != 0:
			self.cbox.log.info("could not retrieve luks uuid (%s): %s", 
					(self.device, stderr.strip()))
			return None
		return stdout.strip()

	
	def __get_non_luks_uuid(self):
		"""return UUID for ext2/3 and vfat filesystems"""
		proc = subprocess.Popen(
			shell=False,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			args=[self.cbox.prefs["Programs"]["blkid"],
				"-s", "UUID",
				"-o", "value",
				"-c", os.devnull,
				"-w", os.devnull,
				self.device])
		(stdout, stderr) = proc.communicate()
		## execution failed?
		if proc.returncode != 0:
			self.cbox.log.info("retrieving of partition type (" + str(self.device) \
					+ ") via 'blkid' failed: " + str(stderr.strip()) \
					+ " - maybe it is encrypted?")
			return None
		## return output of blkid
		return stdout.strip()


	def __get_type_of_partition(self):
		"""Retrieve the type of the given partition.
		
		see cryptobox.core.container.CONTAINERTYPES
		"""
		if self.__is_luks_partition():
			return CONTAINERTYPES["luks"]
		type_of_partition = self.__get_type_id_of_partition()
		if type_of_partition in FSTYPES["plain"]:
			return CONTAINERTYPES["plain"]
		if type_of_partition in FSTYPES["swap"]:
			return CONTAINERTYPES["swap"]
		return CONTAINERTYPES["unused"]


	def __get_type_id_of_partition(self):
		"returns the type of the partition (see 'man blkid')"
		proc = subprocess.Popen(
			shell = False,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [ self.cbox.prefs["Programs"]["blkid"],
				"-s", "TYPE",
				"-o", "value",
				"-c", os.devnull,
				"-w", os.devnull,
				self.device ])
		(stdout, stderr) = proc.communicate()
		if proc.returncode == 0:
			## we found a uuid
			return stdout.strip()
		elif proc.returncode == 2:
			## failed to find the attribute - no problem
			return None
		else:
			## something strange happened
			self.cbox.log.warn("retrieving of partition type via 'blkid' failed: %s" % \
					(stderr.strip(), ))
			return None


	def __is_luks_partition(self):
		"check if the given device is a luks partition"
		proc = subprocess.Popen(
			shell = False,
			stdin = None,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["cryptsetup"],
				"--batch-mode",
				"isLuks",
				self.device])
		proc.wait()
		return proc.returncode == 0


	def __get_mount_point(self):
		"return the name of the mountpoint of this volume"
		return os.path.join(self.cbox.prefs["Locations"]["MountParentDir"], self.name)


	def __mount_luks(self, password):
		"mount a luks partition"
		if not password:
			raise CBInvalidPassword("no password supplied for luksOpen")
		if self.is_mounted():
			raise CBVolumeIsActive("this container is already active")
		self.__umount_luks()
		self.__clean_mount_dirs()
		if not os.path.exists(self.__get_mount_point()):
			self.__create_mount_directory(self.__get_mount_point())
		if not os.path.exists(self.__get_mount_point()):
			err_msg = "Could not create mountpoint (%s)" % (self.__get_mount_point(), )
			self.cbox.log.error(err_msg)
			raise CBMountError(err_msg)
		self.cbox.send_event_notification("premount", self.__get_event_args())
		proc = subprocess.Popen(
			shell = False,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"cryptsetup",
				"luksOpen",
				self.device,
				self.name,
				"--batch-mode"])
		proc.stdin.write(password)
		(output, errout) = proc.communicate()
		if proc.returncode != 0:
			err_msg = "Could not open the luks mapping: %s" % (errout.strip(), )
			self.cbox.log.warn(err_msg)
			raise CBMountError(err_msg)
		proc = subprocess.Popen(
			shell = False,
			stdin = None,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"mount",
				os.path.join(self.__dmDir, self.name),
				self.__get_mount_point()])
		proc.wait()
		if proc.returncode != 0:
			err_msg = "Could not mount the filesystem: %s" % (proc.stderr.read().strip(), )
			self.cbox.log.warn(err_msg)
			raise CBMountError(err_msg)
		## chmod the mount directory to 0777 - this is the easy way to avoid problems
		## this only works for ext2/3 - vfat silently ignore it
		## we mounted vfat partitions with umask=0000
		try:
			os.chmod(self.__get_mount_point(), 0777)
		except OSError:
			self.cbox.log.warn("Failed to set write permission for the mount directory")
		self.cbox.send_event_notification("postmount", self.__get_event_args())


	def __umount_luks(self):
		"umount a luks partition"
		self.cbox.send_event_notification("preumount", self.__get_event_args())
		if self.is_mounted():
			proc = subprocess.Popen(
				shell = False,
				stdin = None,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE,
				args = [
					self.cbox.prefs["Programs"]["super"],
					self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
					"umount",
					self.__get_mount_point()])
			proc.wait()
			if proc.returncode != 0:
				err_msg = "Could not umount the filesystem: %s" % (proc.stderr.read().strip(), )
				self.cbox.log.warn(err_msg)
				raise CBUmountError(err_msg)
		if os.path.exists(os.path.join(self.__dmDir, self.name)):
			proc = subprocess.Popen(
				shell = False,
				stdin = None,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE,
				args = [
					self.cbox.prefs["Programs"]["super"],
					self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
					"cryptsetup",
					"luksClose",
					self.name,
					"--batch-mode"])
			proc.wait()
			if proc.returncode != 0:
				err_msg = "Could not remove the luks mapping: %s" % (proc.stderr.read().strip(), )
				self.cbox.log.warn(err_msg)
				raise CBUmountError(err_msg)
		self.cbox.send_event_notification("postumount", self.__get_event_args())


	def __mount_plain(self):
		"mount a plaintext partition"
		if self.is_mounted():
			raise CBVolumeIsActive("this container is already active")
		self.__clean_mount_dirs()
		if not os.path.exists(self.__get_mount_point()):
			self.__create_mount_directory(self.__get_mount_point())
		if not os.path.exists(self.__get_mount_point()):
			err_msg = "Could not create mountpoint (%s)" % (self.__get_mount_point(), )
			self.cbox.log.error(err_msg)
			raise CBMountError(err_msg)
		self.cbox.send_event_notification("premount", self.__get_event_args())
		proc = subprocess.Popen(
			shell = False,
			stdin = None,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"mount",
				self.device,
				self.__get_mount_point()])
		proc.wait()
		if proc.returncode != 0:
			err_msg = "Could not mount the filesystem: %s" % (proc.stderr.read().strip(), )
			self.cbox.log.warn(err_msg)
			raise CBMountError(err_msg)
		## chmod the mount directory to 0777 - this is the easy way to avoid problems
		## this only works for ext2/3 - vfat silently ignore it
		## we mounted vfat partitions with umask=0000
		try:
			os.chmod(self.__get_mount_point(), 0777)
		except OSError:
			self.cbox.log.warn("Failed to set write permission for the mount directory")
		self.cbox.send_event_notification("postmount", self.__get_event_args())


	def __umount_plain(self):
		"umount a plaintext partition"
		if not self.is_mounted():
			self.cbox.log.info("trying to umount while volume (%s) is not mounted" % \
					self.get_device())
			return
		self.cbox.send_event_notification("preumount", self.__get_event_args())
		proc = subprocess.Popen(
			shell = False,
			stdin = None,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"umount",
				self.__get_mount_point()])
		proc.wait()
		if proc.returncode != 0:
			err_msg = "Could not umount the filesystem: %s" % (proc.stderr.read().strip(), )
			self.cbox.log.warn(err_msg)
			raise CBUmountError(err_msg)
		self.cbox.send_event_notification("postumount", self.__get_event_args())
	

	def __create_plain(self, fs_type="ext3"):
		"make a plaintext partition"
		import threading
		if self.is_mounted():
			raise CBVolumeIsActive(
					"deactivate the partition before filesystem initialization")
		def format():
			"""This function will get called as a seperate thread.

			To avoid the non-sharing cpu distribution between the formatting thread
			and the main interface, we fork and let the parent wait for the child.
			This should be handled using the kernel's threading features.
			"""
			## create a local object - to store different values for each thread
			loc_data = threading.local()
			loc_data.old_name = self.get_name()
			self.set_busy(True, 600)
			## give the main thread a chance to continue
			loc_data.child_pid = os.fork()
			if loc_data.child_pid == 0:
				loc_data.proc = subprocess.Popen(
					shell = False,
					stdin = None,
					stdout = subprocess.PIPE,
					stderr = subprocess.PIPE,
					args = [
							self.cbox.prefs["Programs"]["nice"],
							self.cbox.prefs["Programs"]["mkfs"],
							"-t", fs_type, self.device])
				loc_data.proc.wait()
				## wait to allow error detection
				if loc_data.proc.returncode == 0:
					time.sleep(5)
				## skip cleanup stuff (as common for sys.exit)
				os._exit(0)
			else:
				os.waitpid(loc_data.child_pid, 0)
				try:
					self.set_name(loc_data.old_name)
				except CBNameIsInUse:
					pass
				self.set_busy(False)
		bg_task = threading.Thread(target=format)
		bg_task.setDaemon(True)
		bg_task.start()
		time.sleep(3)
		## if the thread exited very fast, then it failed
		if not bg_task.isAlive():
			raise CBCreateError("formatting of device (%s) failed out " % self.device \
					+ "of unknown reasons")


	def __create_luks(self, password, fs_type="ext3"):
		"""Create a luks partition.
		"""
		import threading
		if not password:
			raise CBInvalidPassword("no password supplied for new luks mapping")
		if self.is_mounted():
			raise CBVolumeIsActive("deactivate the partition before filesystem initialization")
		## remove any potential open luks mapping
		self.__umount_luks()
		## create the luks header
		proc = subprocess.Popen(
			shell = False,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"cryptsetup",
				"luksFormat",
				self.device,
				"--batch-mode",
				"--cipher", self.cbox.prefs["Main"]["DefaultCipher"],
				"--iter-time", "2000"])
		proc.stdin.write(password)
		(output, errout) = proc.communicate()
		if proc.returncode != 0:
			err_msg = "Could not create the luks header: %s" % (errout.strip(), )
			self.cbox.log.error(err_msg)
			raise CBCreateError(err_msg)
		## open the luks container for mkfs
		proc = subprocess.Popen(
			shell = False,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"cryptsetup",
				"luksOpen",
				self.device,
				self.name,
				"--batch-mode"])
		proc.stdin.write(password)
		(output, errout) = proc.communicate()
		if proc.returncode != 0:
			err_msg = "Could not open the new luks mapping: %s" % (errout.strip(), )
			self.cbox.log.error(err_msg)
			raise CBCreateError(err_msg)
		def format_luks():
			"""This function will get called as a seperate thread.

			To avoid the non-sharing cpu distribution between the formatting thread
			and the main interface, we fork and let the parent wait for the child.
			This should be handled using the kernel's threading features.
			"""
			## create a local object - to store different values for each thread
			loc_data = threading.local()
			loc_data.old_name = self.get_name()
			self.set_busy(True, 600)
			loc_data.child_pid = os.fork()
			if loc_data.child_pid == 0:
				## make the filesystem
				loc_data.proc = subprocess.Popen(
					shell = False,
					stdin = None,
					stdout = subprocess.PIPE,
					stderr = subprocess.PIPE,
					args = [
						self.cbox.prefs["Programs"]["nice"],
						self.cbox.prefs["Programs"]["mkfs"],
						"-t", fs_type,
						os.path.join(self.__dmDir, self.name)])
				loc_data.proc.wait()
				## wait to allow error detection
				if loc_data.proc.returncode == 0:
					time.sleep(5)
				## skip cleanup stuff (as common for sys.exit)
				os._exit(0)
			else:
				os.waitpid(loc_data.child_pid, 0)
				self.set_name(loc_data.old_name)
				self.set_busy(False)
				## remove the mapping - for every exit status
				self.__umount_luks()
		bg_task = threading.Thread(target=format_luks)
		bg_task.setDaemon(True)
		bg_task.start()
		time.sleep(3)
		## if the thread exited very fast, then it failed
		if not bg_task.isAlive():
			raise CBCreateError("formatting of device (%s) failed out " % self.device \
					+ "of unknown reasons")


	def __clean_mount_dirs(self):
		"""	remove all unnecessary subdirs of the mount parent directory
			this should be called for every (u)mount	"""
		subdirs = os.listdir(self.cbox.prefs["Locations"]["MountParentDir"])
		for one_dir in subdirs:
			abs_dir = os.path.join(self.cbox.prefs["Locations"]["MountParentDir"], one_dir)
			if (not os.path.islink(abs_dir)) \
					and os.path.isdir(abs_dir) \
					and (not os.path.ismount(abs_dir)) \
					and (os.path.isfile(os.path.join(abs_dir,MOUNT_DIR_MARKER))) \
					and (len(os.listdir(abs_dir)) == 1):
				try:
					os.remove(os.path.join(abs_dir, MOUNT_DIR_MARKER))
					os.rmdir(abs_dir)
				except OSError, err_msg:
					## we do not care too much about unclean cleaning ...
					self.cbox.log.info("failed to clean a mountpoint (%s): %s" % \
							(abs_dir, str(err_msg)))
	

	def __create_mount_directory(self, dirname):
		"""create and mark a mount directory
		this marking helps to remove old mountdirs safely"""
		os.mkdir(dirname)
		try:
			mark_file = file(os.path.join(dirname, MOUNT_DIR_MARKER), "w")
			mark_file.close()
		except OSError, err_msg:
			## we do not care too much about the marking
			self.cbox.log.info("failed to mark a mountpoint (%s): %s" % (dirname, str(err_msg)))
		

	def __get_event_args(self):
		"""Return an array of arguments for event scripts.
		
		for now supported: pre/post-mount/umount events
		"""
		type_text = [e for e in CONTAINERTYPES.keys()
				if CONTAINERTYPES[e] == self.get_type()][0]
		return [self.get_device(), self.get_name(), type_text, self.__get_mount_point()]

