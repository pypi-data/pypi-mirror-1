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
import math
from optparse import OptionParser

from vhybridize.utils  import *
from vhybridize.config import *

DEF_DIGITS = 0


def filter_chunks(opt, chunks):
    min, max = opt.min_length, opt.max_length
    if max:
	def good_p(pair):
	    name, chunk = pair
	    return min <= len(fasta_sequence(chunk)) <= max
    elif min:
	def good_p(pair):
	    name, chunk = pair
	    return min <= len(fasta_sequence(chunk))
    else:
	return chunks

    return filter(good_p, chunks)


def assign_names(opt, chunks):
    if opt.numeric:
	if opt.nb_digits:
	    nb_digits = opt.nb_digits
	else:
	    nb_digits = int(math.ceil(math.log10(len(chunks)-1)))
	return [("%0*d" % (nb_digits, i), c) for i, c in enumerate(chunks)]
    else:
	# check that all the names are unique
	names = {}
	for c in chunks:
	    name = fasta_name(c)
	    names[name] = names.get(name, 0) + 1
	if len(names) != len(chunks):
	    dups = [k for k,v in filter(lambda p:p[1]>1, names.items())]
	    print "can't find a unique name for each sequence"
	    print "those names are duplicated:", dups
	    print "please rename your sequences or try with -n"
	    sys.exit(1)

	return [(fasta_name(c), c) for c in chunks]


def parse_args():
    desc = ("Split a multi-fasta file into several mono-fasta files. "
	    "This software is part of the vhybridze %s package." % VERSION)
    parser = OptionParser(usage="%prog [options] FASTA-FILE OUTPUT-DIR",
                          version="%prog " + VERSION,
			  description=desc)

    parser.add_option("-n", "--numeric",
                      default=False,
                      action="store_true",
                      dest="numeric",
                      help=("use numeric sequential names; default is to"
			    " extract the name from the FASTA header lines"))

    parser.add_option("-d", "--digits",
                      default=DEF_DIGITS,
                      dest="nb_digits",
                      help=("number of digits to use for numeric names; "
			    "default is to use as few digits as possible "
			    "to keep lexical and numeric order the same"),
		      type="int")

    parser.add_option("-f", "--filter-min",
                      default=0,
                      dest="min_length",
                      help=("don't output sequences shorter than MIN_LENGTH;"
			    " filtering is done after name assignation so"
			    " numeric names might have gaps but the"
			    " positions will be the same as in the"
			    " multi-fasta file"),
		      type="int")

    parser.add_option("-F", "--filter-max",
                      default=0,
                      dest="max_length",
                      help=("don't output sequences longer than MAX_LENGTH;"
			    " filtering is done after name assignation so"
			    " numeric names might have gaps but the"
			    " positions will be the same as in the"
			    " multi-fasta file"),
		      type="int")

    opt, args = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
        sys.exit(1)
    return opt, args


def main():
    opt, args = parse_args()

    if not os.path.isdir(args[1]):
	os.mkdir(args[1])
    chunks = split_multi_fasta(open(args[0]).read())
    
    for name, chunk in filter_chunks(opt, assign_names(opt, chunks)):
	open(os.path.join(args[1], name+".fas"), "w").write(chunk+"\n\n")


if __name__ == "__main__":
    main()
    
