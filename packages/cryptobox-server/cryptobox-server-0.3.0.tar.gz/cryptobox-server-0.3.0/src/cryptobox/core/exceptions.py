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
exceptions of the cryptobox package
"""

__revision__ = "$Id"


class CBError(Exception):
	"""base class for exceptions of the cryptobox"""
	pass


class CBConfigError(CBError):
	"""any kind of error related to the configuration of a cryptobox"""
	pass


class CBConfigUnavailableError(CBConfigError):
	"""config file/input was not available at all"""
	
	def __init__(self, source=None):
		self.source = source
	
	def __str__(self):
		if self.source:
			return "failed to access the configuration of the cryptobox: %s" % self.source
		else:
			return "failed to access the configuration of the cryptobox"


class CBConfigUndefinedError(CBConfigError):
	"""a specific configuration setting was not defined"""

	def __init__(self, section, name=None):
		self.section = section
		self.name = name
	
	def __str__(self):
		"""Output the appropriate string: for a setting or a section.
		"""
		if self.name:
			# setting
			return "undefined configuration setting: [" + str(self.section) \
					+ "]->" + str(self.name) + " - please check your configuration file"
		else:
			# section
			return "undefined configuration section: [" + str(self.section) \
					+ "] - please check your configuration file"
			


class CBConfigInvalidValueError(CBConfigError):
	"""a configuration setting was invalid somehow"""

	def __init__(self, section, name, value, reason):
		self.section = section
		self.name = name
		self.value = value
		self.reason = reason
	
	
	def __str__(self):
		"""Return the error description.
		"""
		return "invalid configuration setting [%s]->%s (%s): %s" % \
				(self.section, self.name, self.value, self.reason)


class CBEnvironmentError(CBError):
	"""some part of the environment of the cryptobox is broken
	e.g. the wrong version of a required program
	"""

	def __init__(self, desc):
		self.desc = desc

	def __str__(self):
		"""Return the error description.
		"""
		return "misconfiguration detected: %s" % self.desc


class CBContainerError(CBError):
	"""Any error raised while manipulating a cryptobox container.
	"""

	
class CBCreateError(CBContainerError):
	"""Raised if a container could not be created (formatted).
	"""
	pass

class CBVolumeIsActive(CBContainerError):
	"""Raised if a container was active even if it may not for a specific action.
	"""
	pass

class CBInvalidName(CBContainerError):
	"""Raised if someone tried to set an invalid container name.
	"""
	pass

class CBNameIsInUse(CBContainerError):
	"""Raised if the new name of a container is already in use.
	"""
	pass

class CBInvalidType(CBContainerError):
	"""Raised if a container is of an invalid type for a choosen action.
	"""
	pass

class CBInvalidPassword(CBContainerError):
	"""Someone tried to open an ecnrypted container with the wrong password.
	"""
	pass

class CBChangePasswordError(CBContainerError):
	"""Changing of the password of an encrypted container failed.
	"""
	pass

class CBMountError(CBContainerError):
	"""Failed to mount a container.
	"""
	pass

class CBUmountError(CBContainerError):
	"""Failed to umount a container.
	"""
	pass

