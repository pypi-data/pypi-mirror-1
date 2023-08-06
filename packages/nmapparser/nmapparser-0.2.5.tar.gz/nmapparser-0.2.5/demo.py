#!/usr/bin/env python
# Copyright (C) 2007 Guilherme Polo <ggpolo@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
"""
A demo script showing how to use nmapparser.
"""

import sys
from nmapparser import NmapParser

def usage():
    """Show demo usage."""
    print "Usage: %s xmlfile1.xml xmlfile2.xml ..." % __file__

def main(args):
    parser = NmapParser()
    for xmlf in sys.argv[1:]:
        print "%s\nParsing %s" % ('*' * 75, xmlf)
        parser.parse(xmlf)

        if not parser.parsed:
            continue

        print "Options:", parser.options
        print "Finish time:", parser.runstats.finished.time

        h_stats = parser.runstats.hosts
        print "Hosts -> total %s, up: %s, down: %s" % (
            h_stats.total, h_stats.up, h_stats.down)

        for host in parser.host:
            print "Host options:", host.options

            if 'extraports' in  host.options:
                print "Host extraports:", host.ports.extraports

            print "Hostname:", host.hostnames

            if 'ports' not in host.options or \
                'ports' not in host.ports.options:
                continue

            if 'script' in host.ports.ports[0].options:
                print
                print host.ports.ports[0].script[0].output
                print

            print "Host ports info:"
            for p in host.ports.ports:
                print "%7s%9s%6s" % (p.portid, p.state, p.protocol)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(usage())
    main(sys.argv)
