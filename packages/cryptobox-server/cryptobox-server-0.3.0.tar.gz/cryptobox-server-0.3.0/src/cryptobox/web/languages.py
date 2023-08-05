#-*- coding: utf-8 -*-
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

"""supply information about existing languages
"""

__revision__ = "$Id: languages.py 931 2007-03-29 21:32:26Z lars $"

## every language information should contain (name, pluralformat)
LANGUAGE_INFO = {
    "cs": ('Český',	('3', '(n==1) ? 0 : (n>=2 && n< =4) ? 1 : 2')),
    "da": ('Dansk',	('2', '(n != 1)')),
    "de": ('Deutsch',	('2', '(n != 1)')),
    "en": ('English',	('2', '(n != 1)')),
    "es": ('Español',	('2', '(n != 1)')),
    "et": ('Eesti', 	('2', '(n != 1)')),
    "fi": ('Suomi',	('2', '(n != 1)')),
    "fr": ('Français',	('2', '(n != 1)')),
    "hu": ('Magyar',	('1', '0')),
    "hr": ('Hrvatski',	('3', '(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)')),
    "it": ('Italiano',	('2', '(n != 1)')),
    "ja": ('日本語',	('1', '0')),
    "nl": ('Nederlands',	('2', '(n != 1)')),
    "pl": ('Polski',	('3', '(n==1 ? 0 : n%10>=2 && n%10< =4 '
            + '&& (n%100<10 || n%100>=20) ? 1 : 2)')),
    "pt": ('Português',	('2', '(n != 1)')),
    "ru": ('Русский',	('3', '(n%10==1 && n%100!=11 ? 0 : '
            + 'n%10>=2 && n%10< =4 && (n%100<10 || n%100>=20) ? 1 : 2)')),
    "sl": ('Slovensko',	('4', '(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || '
            + 'n%100==4 ? 2 : 3)')),
    "sv": ('Svenska',	('2', '(n != 1)')),
    }

