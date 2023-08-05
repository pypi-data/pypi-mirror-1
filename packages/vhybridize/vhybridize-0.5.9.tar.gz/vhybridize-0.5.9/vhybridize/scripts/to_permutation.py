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

# TODO: permutation compression

def parse_args():
    desc = ("Extract 'dumb' permutations out of a set of .vhy files."
	    " Basicaly, only the probes that apear exactly once per file"
	    " are kept. "
	    "This software is part of the vhybridze %s package." % VERSION)
    parser = OptionParser(usage="%prog [options] FILE1 [FILE2 ...]",
                          version="%prog " + VERSION,
			  description=desc)

    parser.add_option("-v", "--verbose",
                      default=False,
                      action="store_true",
                      dest="verbose",
                      help="print which signal is deleted and why")

    opt, args = parser.parse_args()
    if not args:
        parser.print_help()
        sys.exit(1)
    return opt, args


def print_del_sigs(sigs, why):
    print "# deleted", len(sigs), "probes:", why
    sigs.sort()
    print "#", ", ".join(sigs)


def print_kept_sigs(sigs, nb_orig):
    print "# kept", len(sigs), "probes from", nb_orig
    sigs.sort()
    print "#", ", ".join(sigs)


def main():
    opt, args = parse_args()

    sections = load_multi_vhy(args[0])
    for f in args[1:]:
	sections += load_multi_vhy(f)

    # we can extract a permutation in two pass:
    #   1) count occurences per segment and kick all dups
    #   2) count occurences on all seqs and kick all sig where
    #      nb_occ != len(seqs)
    # The permutation in a "dumb" one where no effort is made to find
    # homologs of dups, we just kick anything that can't yeild an obvious
    # permutation

    # first pass: kill the dups
    kill_h = {}
    for recs, name in sections:
	seen_h = {}
	for probe in map(probe_name, recs):
	    if seen_h.has_key(probe):
		kill_h[probe] = True
	    else:
		seen_h[probe] = True

    def notdup_p(rec):
	return not kill_h.has_key(probe_name(rec))
    
    sections = [(filter(notdup_p, recs), name)
		for recs, name in sections]

    # second pass: kill the missings
    nb_occ_h = {}
    for recs, name in sections:
	for sig in map(probe_name, recs):
	    nb_occ_h[sig] = nb_occ_h.get(sig, 0) + 1

    nb_seq = len(sections)
    def everywhere_p(rec):
	return nb_occ_h[probe_name(rec)] == nb_seq
    
    sections = [(filter(everywhere_p, recs), name)
		for recs, name in sections]

    print build_multi_file_content(sections)

    if opt.verbose:
	print_del_sigs(kill_h.keys(), "duplicated")
	missings = filter(lambda sig:nb_occ_h[sig] < nb_seq,
			  nb_occ_h.keys())
	print_del_sigs(missings, "missing on some genomes")
	kept = map(probe_name, sections[0][0])
	print_kept_sigs(kept, len(kept)+len(missings)+len(kill_h))


if __name__ == "__main__":
    main()
    
