#!/usr/bin/env python

import sys
import getopt
import re

# I know this is not the best re ever for this. On decent amounts of text,
# it is sufficient.
sentence_re = re.compile(r"(?:^|[?!\.:;]?\s+)([A-Z][a-zA-Z\d ,]+[?!\.])")

if len(sys.argv) == 1:
    print >>sys.stderr, "usage: %s <file1> [file2 [fileN ...]]" % sys.argv
    sys.exit(1)

for filename in sys.argv[1:]:
    fp = file(filename, "r")
    paragraph = []
    try:
        for line in fp:
            line = "".join(c for c in line.rstrip()
                    if 31 < ord(c) < 127)
            if not line:
                for match in sentence_re.finditer(" ".join(paragraph)):
                    print match.group(1)
                paragraph = []
            else:
                paragraph.append(line)
        if paragraph:
            for match in sentence_re.finditer(" ".join(paragraph)):
                print match.group(1)
    finally:
        fp.close()
