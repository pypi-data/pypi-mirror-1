#!/usr/bin/env python

import sys
import itertools
import re

if len(sys.argv) > 1:
    fp = open(sys.argv[1])
else:
    fp = sys.stdin

lines = fp.readlines()

beg = re.compile('^\$sociable_known_sites')
end = re.compile('^\);')
def find_beginning(item):
    return not beg.match(item)

def find_end(item):
    return not end.match(item)
    
def dropbefore(lines):
    for line in itertools.dropwhile(find_beginning, lines):
        yield line

def dropafter(lines):
    for line in itertools.takewhile(find_end, lines):
        yield line

start_item = re.compile(r"""^\t('[^']*') => Array\(""")
favicon_item = re.compile(r"""\t\t('favicon') => '([^']*)',""")
mid_item = re.compile(r"""\t\t('[^']*') => ('[^']*'),""")
end_item = re.compile(r"""\t\),""")

def start_item_handle(m):
    print "\t%s: {" % (m.groups()[0],)

def favicon_item_handle(m):
    k, v = m.groups()
    print "\t\t%s: turbogears.url('/tg_widgets/tgsociable/images/%s')," % (k, v)

def mid_item_handle(m):
    k, v = m.groups()
    v = v.replace("&amp;", "&")
    print "\t\t%s: %s," % (k, v)

def end_item_handle(m):
    print "\t},"

handlers = [
    (start_item, start_item_handle),
    (favicon_item, favicon_item_handle),
    (mid_item, mid_item_handle),
    (end_item, end_item_handle),
]

def handle_lines(lines):
    for line in dropafter(dropbefore(lines)):
        line = line.rstrip()
        #print line
        for regex, handler in handlers:
            m = regex.search(line)
            if m:
                handler(m)
                break

print "import turbogears"
print "all_sites = {"
handle_lines(lines)
print "}"
