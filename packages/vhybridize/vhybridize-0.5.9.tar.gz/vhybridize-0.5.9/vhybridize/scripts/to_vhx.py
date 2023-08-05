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
    desc = ("Convert one or more .vhy files in .vhx format. This is just"
	    " the ordered sequence of probes with Fasta like sections"
	    " separators. "
	    "This software is part of the vhybridze %s package." % VERSION)
    parser = OptionParser(usage="%prog [options] FILE1 [FILE2 ...]",
                          version="%prog " + VERSION,
			  description=desc)

    parser.add_option("-c", "--comma",
                      default=False,
                      action="store_true",
                      dest="comma",
                      help=("seperate probe names with a comma"
			    "; default is a newline"))

    opt, args = parser.parse_args()
    if not args:
        parser.print_help()
        sys.exit(1)
    return opt, args

def main():
    opt, args = parse_args()

    sections = load_multi_vhy(args[0])
    for f in args[1:]:
	sections += load_multi_vhy(f)

    sep = ["\n", ", "][opt.comma]
    for recs, name in sections:
	print ">", name
	print sep.join([r[VHY_PROBE] for r in recs]) + "\n"


if __name__ == "__main__":
    main()
    
