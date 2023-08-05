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
# Dependencies: clearsilver(python), cherrypy, python-configobj
#

from distutils.core import setup
import distutils.sysconfig
import os

## define some strings (not patterns) to exclude specific files or directories
IGNORE_FILES = [ '.svn', 'intl' ]

## define the data destination directory (below the python directory - for debian this gets overridden the rules file)
pydir = distutils.sysconfig.get_python_lib()
## remove installation prefix to get relative path
pydir = pydir.replace(distutils.sysconfig.get_config_var("prefix") + os.path.sep, '')
pydir = os.path.join(pydir, 'cryptobox')

## shared data dir
datadir = os.path.join('share', 'cryptobox-server')
## doc dir
docdir = os.path.join('share', 'doc', 'cryptobox-server')
## configuration directory
confdir = os.path.join(os.path.sep, 'etc', 'cryptobox-server')


def listfiles(prefix, src):
	"""create a list of files below a directory recursively

	If the src contains more then one path element (multiple levels), then only the
	last one (basename part) is added to the prefix path (e.g.: 'dest','src1/src2' will
	create a list below 'dest/src2').
	The result is a list of tuples: (destination, [srcfiles,...]).
	This is the datatype expected by 'data_files' in setup."""
	## we will not add the 'dirname' part of srcdir to the destination
	src_dir, src_base = os.path.split(src)
	## add the files of this directory
	result = [(os.path.join(prefix, src_base), [ os.path.join(src, f)
			for f in os.listdir(src)
			if os.path.isfile(os.path.join(src, f)) \
					and not f in IGNORE_FILES ])]
	## add the files in subdirectories
	for d in os.listdir(src):
		if os.path.isdir(os.path.join(src,d)) and not d in IGNORE_FILES:
			result.extend(listfiles(
					os.path.join(prefix,src_base), os.path.join(src, d)))
	return result
		
		
def getdatafiles(prefix, dirs):
	filelist = []
	for d in dirs:
		if os.path.isdir(d):
			filelist.extend(listfiles(prefix, d))
		else:
			filelist.append((prefix, [d]))
	return filelist


def get_language_files(prefix):
	"""return a destination-file mapping for all compiled language files (*.po)
	"""
	import sys
	mapping = []
	## find all language directories
	intl_dirs = []
	for (root, dirs, files) in os.walk(os.getcwd()):
		if 'intl' in dirs:
			intl_dirs.append(os.path.join(root, 'intl'))
	for i_dir in intl_dirs:
		for lang_dir in [os.path.join(i_dir, e)
				for e in os.listdir(i_dir)
				if os.path.isdir(os.path.join(i_dir, e)) and (not e in IGNORE_FILES)]:
			po_files = [ os.path.join(lang_dir, e)
						for e in os.listdir(lang_dir)
						if os.path.isfile(os.path.join(lang_dir, e)) \
								and (e[-3:] == '.po') ]
			lang_files = []
			for po_file in po_files:
				if compile_po_file(po_file):
					lang_files.append(po_file[:-3] + ".mo")
				else:
					sys.stderr.write("Failed to compile language file: %s\n" % po_file)
			mapping.append((os.path.join(
				prefix, os.path.basename(lang_dir), 'LC_MESSAGES'), lang_files))
	return mapping


def compile_po_file(po_file):
	"""compile the binary mo file out of a po file
	"""
	import subprocess
	return subprocess.call( [ "msgfmt", "-o", po_file[:-3] + ".mo", po_file ] ) == 0


setup(
	name	= 'cryptobox-server',
	version	= '0.3.0',
	description	= 'webinterface for handling encrypted disks',
	author	= 'Sense.Lab e.V.',
	author_email	= 'info@cryptobox.org',
	maintainer	= 'Lars Kruse',
	maintainer_email	= 'devel@sumpfralle.de',
	license	= 'GPL',
	url	= 'http://cryptobox.org',
	packages	= [ 'cryptobox', 'cryptobox.core', 'cryptobox.web',
			'cryptobox.plugins', 'cryptobox.tests' ],
	data_files	= getdatafiles(datadir, ['templates', 'www-data', 'plugins']) + 
		getdatafiles(confdir, [os.path.join('conf-examples', 'cryptobox.conf')]) + 
		getdatafiles(os.path.join(confdir, 'events.d'), [
				os.path.join('event-scripts', 'README'),
				os.path.join('event-scripts', '_event_scripts_')]) + 
		getdatafiles(docdir, ['conf-examples', 'event-scripts', 'README', 'changelog',
				'LICENSE', 'copyright', os.path.join('doc', 'html'), 'README.davfs',
				'README.samba', 'README.proxy', 'README.ssl' ]) +
		getdatafiles(os.path.join(docdir, 'conf-examples'), 
				[os.path.join('debian', 'cryptobox-server.init')]) +
		get_language_files(os.path.join('share', 'locale')),
	package_dir	= { '': 'src' },
	scripts	= [ os.path.join('bin', 'CryptoBoxWebserver'),
			os.path.join('bin', 'CryptoBoxRootActions') ],
	classifiers	= [
		'Development Status :: 2 - Beta',
		'Environment	:: Web Environment',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Topic :: System :: Systems Administration',
		'Operating System :: POSIX',
		'Operating System :: Unix',
		'Programming Language :: Python'],
	)

