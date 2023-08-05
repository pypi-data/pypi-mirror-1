#!/usr/bin/env python
"""
Cli Position checker - example & test for pyseo.poschecker.*

Usage:
0. cd to some directory
1. Create file named 'domain.txt' in current directory. Place into this file only one line: domain name to check (WITHOUT www.)
2. Create file named 'phases.txt'. Place there (in UTF-8) search queries you want to check.
3. Make shure you have permissions to write to 'posstats.txt' file in current directory.
4. run `python /full/path/to/poschecker-cli/poschecker.py`
5. Go have some tea.
6. If everything goes ok (you are happy man!) current site status would be appended to posstats.txt file.

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

import time
import sys

import pyseo.poschecker as poschecker
import pyseo.poschecker.yandex as yandex
import pyseo.poschecker.google_com as google_com
import pyseo.poschecker.google_ru as google_ru

# 1: open file domain
try:
    # damn, when did python 2.5 would be stable everywhere?
    # I realy need with istruction
    f = open('domain.txt', 'r')
    domain = f.readline().strip()
except:
    print "You have problems with 'domain.txt' file"
    raise

# 1: open phases file
try:
    f = open('phases.txt')
    phases = []
    line = f.readline()
    while (line):
        phases.append(line.strip())
        line = f.readline()
except:
    print "You have problems with 'phases.txt' file"
    raise

ret = []

# 3: check positions
ne = 3 # number of engines
# create checkers:
checkers = (
    yandex.YandexChecker(),
    google_com.GooglecomChecker(),
    google_ru.GoogleruChecker()
)
i  = 1

for p in phases:
    for checker in checkers:
        print ("Progessing %i of %i (query '%s' in %s)" %
            (i, len(phases)*ne, p, checker.name))
        i += 1
        try:
            r = checker.check_position(domain, p)
            if r: 
                # wow, we found it. User must be happy
                r['phase'] = p
                r['se'] = checker.name
            else:
                # so, you need to work with this site
                r = {
                    'position': 0,
                    'phase': p,
                    'se': checker.name,
                    'page': ''
                }
            ret.append(r)
        except KeyboardInterrupt:
            sys.exit()
        except:
            print "Some error"
            # TODO: print actual error
        

# 4: output:
try:
    f = open('posstats.txt', 'a')
    f.write("\n" + time.strftime("%d.%m.%Y", time.localtime()) + "\n")
    for r in ret:
        f.write(r['se'] + "\t" + \
            str(r['phase']) + "\t" +\
            str(r['position']) + "\t" \
            + str(r['page']) + "\n")
    f.close()
except:
    print "You (or me?) have problems with 'posstats.txt' file"
    raise

print "All done more or less succesfully"
