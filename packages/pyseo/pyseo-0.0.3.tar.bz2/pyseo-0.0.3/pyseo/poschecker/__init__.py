#!/usr/bin/env python
"""
Poschecker - Position Checking Abstract Class

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

2007_10_15:
    Vladimir Rusinov <vladimir@greenmice.info>:
        * first version
"""

# TODO: implement loggers

class PosChecker:
    """
        PosChecker class - abstract class for all position checkers
        NOTE: This is ABSTRACT class
    """
    def __init__(self, **kwargs):
        """ Initialise class
        Possible kwargs:
            (str)proxy - url of http proxy (http://user@pass:proxy:port/). default is ''
            (int)delay - delay between requests in seconds. default is 1
            (str)user_agent - user agent.
                Default is 'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.8.1.6) Gecko/20071005 Firefox/2.0.0.6'
        """
        self._options = kwargs
    
    #_progress = 0;
    
    def _get_option(self, key, default):
        try:
            return self._options['key'];
        except KeyError:
            return default
    
    #def get_progress(self):
    #    return self._progress;
    
    def check_position(self, url, query, **kwargs):
        """ Check site position
        Params:
            (str)url - site to check ('greenmice.info')
            (str)query - query to ask ('Linux SEO Software')
            kwargs: possible arguments:
                (int)deep - deep of checking. Recommended values: 10, 50, 100
        """
        self._progress = 0;

# ===============================================
# tests
if (__name__ == '__main__'):
    print "== PosChecker tests =="
    
    print "Creating PosChecker...",
    mycheker = PosChecker(proxy='', delay=2, debug = 1)
    print "ok"
    
    print "Progress is ",
    print mycheker.get_progress()
