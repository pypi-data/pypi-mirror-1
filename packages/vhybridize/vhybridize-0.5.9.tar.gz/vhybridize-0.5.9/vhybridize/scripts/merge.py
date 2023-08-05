#!/usr/bin/python
#  Copyright (C) 2006-2007 Free Software Foundation

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys
from optparse import OptionParser

from vhybridize.utils  import *
from vhybridize.config import *

def parse_args():
    desc = ("Merge multiple .vhy files. The records are assumed to be "
	    "from the same genome.  A typical usage is multiple runs of "
	    "vhybridize on several computers with each a subset of "
	    "the probes. "
	    "This software is part of the vhybridze %s package." % VERSION)
    parser = OptionParser(usage="%prog [options] FILE1 [FILE2 ...]",
                          version="%prog " + VERSION,
			  description=desc)

    opt, args = parser.parse_args()
    if not args:
        parser.print_help()
        sys.exit(1)
    return opt, args


def main():
    opt, args = parse_args()

    recs, name = load_vhy(args[0])
    for f in args[1:]:
	recs += load_vhy(f)[0]
    print build_file_content(recs, name)


if __name__ == "__main__":
    main()
