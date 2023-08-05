#!/bin/sh
#
#  Copyright (c) 02005 sense.lab <senselab@systemausfall.org>
#
#  License:  This script is distributed under the terms of version 2
#            of the GNU GPL. See the LICENSE file included with the package.
#

grep "TODO" $(find "$(dirname $0)/.." -type f | grep -v "\.svn" | grep -v "$(basename $0)") 
