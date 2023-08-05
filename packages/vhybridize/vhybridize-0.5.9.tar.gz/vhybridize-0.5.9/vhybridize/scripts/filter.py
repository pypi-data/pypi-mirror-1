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
    desc = ("Filter records from a .vhy files."
	    "This software is part of the vhybridze %s package." % VERSION)
    parser = OptionParser(usage="%prog [options] FILE",
                          version="%prog " + VERSION,
			  description=desc)

    parser.add_option("-i", "--identity",
                      default=0,
                      dest="min_id",
                      help="minimum %% identity for an occurence",
                      type="float")

    parser.add_option("-l", "--length",
                      default=0,
                      dest="min_length",
                      help="minimum %% of probes length for an occurence",
                      type="float")

    parser.add_option("-p", "--probe-length",
                      default=0,
                      dest="min_probe_length",
                      help="remove all probes shorter than MIN_PROBE_LENGTH",
                      type="int")


    opt, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)
    return opt, args


def main():
    opt, args = parse_args()

    def filter_sect(sect):
	recs, name = sect
	recs = filter(lambda r:r[VHY_A_ID] >= opt.min_id \
		      and r[VHY_A_LEN] >= opt.min_length \
		      and r[VHY_P_LEN] >= opt.min_probe_length ,
		      recs) 
	return recs, name

    sections = map(filter_sect, load_multi_vhy(args[0]))

    print build_multi_file_content(sections)
    


if __name__ == "__main__":
    main()
    
