#!/usr/bin/env python
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

"""This module handles the unittests of all features.
"""

__revision__ = "$Id"

from cryptobox.tests.base import CommonTestClass
import cryptobox.plugins.manage

class CheckForUndefinedTestCases(CommonTestClass):
	"""here we will add failing test functions for every non-existing testcase"""


def create_testcases():
	"""Create functions that execute unittests for all features.
	"""
	plugins = cryptobox.plugins.manage.PluginManager(None, "../plugins").get_plugins()
	glob_dict = globals()
	loc_dict = locals()
	for plugin in plugins:
		test_class = plugin.get_test_class()
		if test_class:
			## add the testclass to the global dictionary
			glob_dict["unittest" + plugin.get_name()] = test_class
		else:
			subname = "test_existence_%s" % plugin.get_name()
			def test_existence(self):
				"""check if the plugin (%s) contains tests""" % plugin.get_name()
				self.fail("no tests defined for plugin: %s" % plugin.get_name())
			## add this function to the class above
			setattr(CheckForUndefinedTestCases, subname, test_existence)
			#FIXME: the failure output always contains the same name for all plugins


create_testcases()

