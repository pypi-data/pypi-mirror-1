#!/usr/bin/env python
# -*- coding: UTF8 -*-
"""
GoogleruChecker - Position Checking for Google Russian [http://google.ru]

Copyright (c) 2007 GreenMice Solutions [http://greenmice.info]
Copyright (c) 2007 Vladimir Rusinov <vladimir@greenmice.info>

pyseo is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

pyseo is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
Infobiller; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
Fifth Floor, Boston, MA  02110-1301  USA
"""

"""
Changelog:

2007_11_17:
    Vladimir Rusinov <vladimir@greenmice.info>
        * first version
"""

from pyseo.poschecker.google_com import GooglecomChecker

class GoogleruChecker(GooglecomChecker):
    """
        Google.ru Checker - position checking for google (russian)
    """
    
    name = "google.ru"
    
    _url = "http://www.google.ru/search"
    _lang = 'lang_ru'
