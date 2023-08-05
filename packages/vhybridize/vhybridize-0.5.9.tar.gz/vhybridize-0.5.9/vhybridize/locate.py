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


""" Find the location of DNA probes on target genomes. """

import os
import sys
import csv
import re
import time
from shutil   import rmtree
from pprint   import pprint
from optparse import OptionParser
from tempfile import NamedTemporaryFile, mkdtemp
from config   import *
from utils    import *

# FIXME: in various places we can read "marker", it should read
#  "probe" since the semantic of "marker" vs "probe" changed and this
#  script is specifically looking for "probes".

# BLAST params that are common to both bl2seq and blastall
PARAMS = " -F F -W 7 -G 6  -r 1 -E 2  -q -1 "

BL2SEQ_CMD   = ("bl2seq " + PARAMS +
		" -V T -D 1 -p blastn -i '%(query)s' -j '%(target)s'")
BLASTALL_CMD = ("blastall " + PARAMS +
		" -m 8 -p blastn -i '%(query)s' -d '%(target)s'")

# For small input (<150kbp) its faster to use bl2seq, for larger input
# it can be faster to pre-hash the fasta files with formatdb and to
# use blastall.  This is selected from the command line at the moment
#   formatdb -i foo.fas -p F
# TODO: select wich blast depending on input length

NEEDLE_CDM = "needle '%(query)s' '%(target)s' -gapopen 10.0 -gapextend 0.5 -outfile %(out)s -fasta 2>/dev/null"

MIN_ALIGN_LEN = 70.0 # in % of probe length
MIN_IDENTITY = 70.0 # in %

DEF_P_DIR = "probes"
DEF_O_DIR = "output"

needle_hit = 0
needle_non = 0


def call_blast(query, target, blast_cmd):
    cmd = blast_cmd % vars()
    cin, cout = os.popen2(cmd)
    return csv.reader(cout, dialect=csv.excel_tab)

def fasta_body(filename, block=1):
    "for nucleotides fasta files"
    lines = open(filename).read().split(">")[block].split("\n")[1:]
    body = "".join(map(lambda l:l.strip(), lines))
    return body

def call_needle(query, target, out, opt):
    cmd = NEEDLE_CDM % vars()
    if opt.debug:
	print cmd
    if os.system(cmd):
        print "can't execute needle"
        sys.exit(1)

def simirarity(seq1, seq2):
    # both seq must be pre-aligned
    same = 0
    for i, j in zip(seq1, seq2):
	if i == j:
	    same += 1
    return 100.0*same / max(map(len, [seq1, seq2]))

def needle_pos(query, target, opt):
    # yeah we kind of can get this with biopython but the API is too
    # ugly
    tmp = NamedTemporaryFile()
    call_needle(query, target, tmp.name, opt)
    m_align = fasta_body(tmp.name)
    align = fasta_body(tmp.name, 2)
    clean_align = align.replace(".", "")
    target_seq = fasta_body(target)

    start = target_seq.find(clean_align)
    if start == -1:
	raise "can't find align"
    
    return start, start+len(align), simirarity(m_align, align)

def parse(reader):
    """kick all the boring stuff
    records are like that
      # Fields: Query id, Subject id, % identity, alignment length,
      # mismatches, gap openings, q. start, q. end, s. start, s. end,
      # e-value, bit score
    """
    hits = []
    lines = filter(lambda x:x[0][0] != "#",
		   [i for i in reader])
    for i in lines:
	hits.append([float(i[2]), int(i[3]), i[4], i[6],
		     i[7], int(i[8]), int(i[9]), i[10], i[11]])
    return hits

def marker_len(m_path):
    return len(fasta_body(m_path))
    
def filter_hits(hits, m_len, opt):
    """keep only the hits with some significance criterion"""
    return filter(lambda x:x[0] > opt.min_id and \
		  100.0*x[1]/m_len > opt.min_length,
		  hits)

def format_hit(h):
    return [h[0], h[1], h[5], h[6]]

def eta(beg, cur, tot):
    elapsed = time.time()-beg
    if cur != 0:
	return "%.2fs" % (1.0*elapsed / cur * (tot-cur))
    return "NA"

def expand(hit_map, opt):
    if not hit_map.keys():
        sys.stderr.write("no hit found\n")
    
    for k, v in hit_map.items():
	base = relpath_wo_ext(k)
	v = map(lambda h:(min([h[1], h[2]]),
			  max([h[1], h[2]]),
			  ["-", "+"][h[1]<h[2]]+relpath_wo_ext(h[0]),
			  h[3], h[4],
			  marker_len(h[0])
			  ),
		v)
	data = build_file_content(v, base)
	path = os.path.join(opt.o_dir, base+".vhy")
	open(path, "w").write(data)


def print_stats(probes):
    lengths = map(marker_len, probes)
    
    print "nb-markers:", len(m_files)
    print "min length:", min(lengths)
    print "max length:", max(lengths)
    print "avg length:", 1.0*sum(lengths)/len(m_files)


def probe_files(opt):
    "return the list of probe files and the directory where to find them" 
    if os.path.isdir(opt.probeset):
	
	return (map(lambda f:os.path.join(opt.probeset, f),
		    os.listdir(opt.probeset)),
		opt.probeset)
    else:
	probes_dir = mkdtemp()
	chunks = split_multi_fasta(open(opt.probeset).read())
	
	# check that all the names are unique
	names = {}
	for c in chunks:
	    name = fasta_name(c)
	    names[name] = names.get(name, 0) + 1
	if len(names) != len(chunks):
	    dups = [k for k,v in filter(lambda p:p[1]>1, names.items())]
	    print "can't find a unique name for each probe in the probeset"
	    print "those names are duplicated:", dups
	    print "please rename your probes and try again"
	    sys.exit(1)

	# save the chunks
	probes = []
	for c in chunks:
	    path = os.path.join(probes_dir, fasta_name(c)+".fas")
	    open(path, "w").write(c)
	    probes.append(path)
	return (probes, probes_dir)
	

def cleanup_probes_cache(opt, probes_dir):
    if not opt.probeset == probes_dir:
	rmtree(probes_dir)


def compute_probes_order(targets, opt):
    # FIXME: those ugly debug vars can probably be removed
    global needle_hit
    global needle_non

    beg = time.time()
    cmd = opt.blastall and BLASTALL_CMD or BL2SEQ_CMD
    hit_map = {}
    probes, probes_dir = probe_files(opt)
    for i, p_path in enumerate(probes):
	#m_path = os.path.join(opt.m_dir, m)
	p_len = marker_len(p_path)
	p_name = relpath_wo_ext(p_path)
	for j, t in enumerate(targets):
	    t_path = t # os.path.join(T_DIR, t)
	    # TODO: this verbose output should be optional
	    print "============================"
	    print "Probe: ", p_name, "(%d/%d) ETA:%s" % (i+1, len(probes),
						    eta(beg, i, len(probes)))
	    print "Target:", t, "(%d/%d)" % (j+1, len(targets))
	    reader = call_blast(p_path, t_path, cmd)
	    hits = filter_hits(parse(reader), p_len, opt)
	    if hits:
		hit_map[t] = hit_map.get(t, []) \
			     + map(lambda h:[p_path, h[5], h[6],
					     int(100.0*h[1]/p_len),
					     int(h[0])],
				   hits)
	    elif opt.use_needle:
		start, stop, sim = needle_pos(p_path, t_path, opt)
		var = 100.0*abs(stop-start-m_len)/p_len
		if (100.0 - var > opt.min_length) and sim > opt.min_id:
		    hit_map[t] = hit_map.get(t, []) + [ [p_path, start, stop,
							 (100.0-var),
							 (sim)] ]
 		    print "needle hit:", stop - start, var, m_len, sim
		    needle_hit += 1
 		else:
		    needle_non += 1

    expand(hit_map, opt)
    if opt.stats:
	print_stats(probes)
    cleanup_probes_cache(opt, probes_dir)
    
def parse_args():
    desc = ("Find the location of DNA probes on target genomes. "
	    "This software is part of the vhybridze %s package." % VERSION)
    parser = OptionParser(usage="%prog [options] target1 [target2 ...]",
                          version="%prog " + VERSION,
			  description=desc)
    parser.add_option("-p", "--probes",
                      default=DEF_P_DIR,
                      dest="probeset",
                      help=("use probes in PROBESET, either a directory"
			    " with one fasta file per probe or a"
			    " multi-fasta file (default is %s)" % DEF_P_DIR))

    parser.add_option("-o", "--output",
                      default=DEF_O_DIR,
                      dest="o_dir",
                      help="put results in DIR (default is %s)" % DEF_O_DIR,
                      metavar="DIR")

    parser.add_option("-n", "--needle",
                      default=False,
                      action="store_true",
                      dest="use_needle",
                      help="try to align with needle when blast fails")

    parser.add_option("-a", "--blastall",
                      default=False,
                      action="store_true",
                      dest="blastall",
                      help="use blastall insteat of bl2seq, " + \
		           "formatdb must be run on all targets first")

    parser.add_option("-d", "--debug",
                      default=False,
                      action="store_true",
                      dest="debug",
                      help="print debugging messages")

    parser.add_option("-i", "--identity",
                      default=MIN_IDENTITY,
                      dest="min_id",
                      help="minimum %% identity (default %s)" % MIN_IDENTITY,
                      type="float")

    parser.add_option("-l", "--length",
                      default=MIN_ALIGN_LEN,
                      dest="min_length",
                      help=("minimum %% of probes length (default %s)" %
                            MIN_ALIGN_LEN),
                      type="float")

    parser.add_option("-s", "--stats",
                      default=False,
                      action="store_true",
                      dest="stats",
                      help="print probes stats")

    opt, args = parser.parse_args()
    if not args:
        parser.print_help()
        sys.exit(1)
    return opt, args

def main():
    opt, args = parse_args()

    if not os.path.isdir(opt.o_dir):
        os.mkdir(opt.o_dir)

    compute_probes_order(args, opt)
    if opt.use_needle:
	print "needle_hit", needle_hit
	print "needle_non", needle_non

if __name__ == "__main__":
    main()
    
