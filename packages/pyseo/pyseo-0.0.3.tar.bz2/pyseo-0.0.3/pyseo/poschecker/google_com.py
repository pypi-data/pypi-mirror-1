#!/usr/bin/env python
# -*- coding: UTF8 -*-
"""
GooglecomChecker - Position Checking for Google (Intertational) [http://google.com]

Please note, that nowdays google's search results is personalised.
So, results of all Google*Checkers usually would differ from results
that you can see in your browser.

This module are not using personalised search (it just rejects all cookies).

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

import logging
import time
import urllib
import urllib2
import random
import gzip
import StringIO
#import re

from BeautifulSoup import BeautifulSoup as BSoup

from pyseo.poschecker import PosChecker

# TODO: implement loggers

class GooglecomChecker(PosChecker):
    """
        Google.com Checker - position checking for yandex
    """
    
    name = "google.com"
    
    _url = "http://www.google.com/search"
    _lang = ''
    
    def check_position(self, url, query, **kwargs):
        """
        Check site position in Yandex
        For more details see help for PosChecker class
        """
        # TODO: IMPLEMENT proxy support
        #self._progress = 0;
        
        depth = self._get_option('depth', 100)
        p = 0 # page
        i = 1 # position
        referrer = 'http://google.com/'
        while (i < depth):
            time.sleep(self._get_option('delay', random.randrange(3, 10))) # sleep some time
            
            # http://www.google.ru/search?q=phase&complete=1&hl=en&newwindow=1&start=10&sa=N
            # create request string
            if (p == 0):
                data = {'q': query, 'hl': 'en', 'lr': self._lang}
            else:
                data = {'q': query, 'hl': 'en', 'lr': self._lang, 'complete': '1', 'newwindow': '1', 'start': str(p*10), 'sa': 'N'}
            enc_data = urllib.urlencode(data)
            req_str = self._url + "?" + enc_data;
            logging.debug("request string: " + req_str);
            
            # get page:
            req = urllib2.Request(req_str)
            req.add_header('Referer', referrer)
            req.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.8.1.6) Gecko/20071005 Firefox/2.0.0.6')
            req.add_header('Accept', 'Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5')
            req.add_header('Accept-Language', 'ru,en-us')
            req.add_header('Accept-Encoding', 'gzip,deflate')
            #req.add_header('Accept-Encoding', 'deflate')
            req.add_header('Accept-Charset', 'windows-1251,utf-8;q=0.7,*;q=0.7')
            req.add_header('Keep-Alive', '300')
            req.add_header('Connection', 'keep-alive')
            
            f = urllib2.urlopen(req)
            page = f.read()
            if f.headers.get('content-encoding', None) == 'gzip':
                page = gzip.GzipFile(fileobj=StringIO.StringIO(page)).read()
            f.close()

            # parse page:
            soup = BSoup(page)
            
            for div in soup.findAll('div', {'class': 'g'}):
                link = div.find('a')
                a = link['href']
                domain = a.split("/")[2]
                if (domain[0:4] == 'www.'):
                    domain = domain[4:]
                if (domain == url):
                    ret = {
                        'position': i,
                        'url': url,
                        'page': a
                    }
                    return ret
                
                i += 1
        
            # loop in page:
            #ol = soup.ol
            #for li in ol.findAll("div"):
            #    s = li.find('span', style='color:#060;').string
            #    domain = self._domain_re.search(s).groups()[0].strip()
            #    a = li.find('a')['href']
            #    domain = domain.split("/")[0]
            #    if (domain[0:4] == 'www.'):
            #        domain = domain[4:]
            #    if (domain == url):
            #        ret = {
            #            'position': i,
            #            'url': url,
            #            'page': a
            #        }
            #        return ret
            #    i += 1
            p += 1
            referrer = req_str
