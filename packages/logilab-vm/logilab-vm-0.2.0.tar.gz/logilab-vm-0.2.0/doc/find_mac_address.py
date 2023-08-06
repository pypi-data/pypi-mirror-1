#!/usr/bin/python
import os, re
import random
import sys

BASEADDR="52:54:00:"
r = re.compile(r'.*macaddr=(?P<macaddr>..:..:..:..:..:..).*')
addrs = set([r.match(line).group('macaddr') for line in os.popen("ps aux").readlines() if r.match(line)])

while 1:
    rands = ":".join(["%02X"%(random.randint(0,255)) for i in range(3)])
    addr = BASEADDR + rands
    if addr not in addrs:
        print addr
	sys.exit(0)

