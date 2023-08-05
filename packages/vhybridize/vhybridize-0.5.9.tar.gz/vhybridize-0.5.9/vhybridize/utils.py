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
import string
from config import *

def split_multi_fasta(data):
    "return a list of fasta records from the body of a multi-fasta"
    return [">"+r for r in filter(lambda r:r,
				  map(string.strip,
				      data.split(">")))]

def fasta_head(data):
    return data.split(">")[1].split("\n")[0].strip()


def fasta_file_head(path):
    return fasta_head(open(path).read())



def fasta_name(data):
    return filter(lambda f:f,
		  map(string.strip, fasta_head(data).split()))[0]


def fasta_sequence(data):
    """Return the concatenated nucleotide (or peptide) sequence as a
    string.  If data is a multi-fasta, only the first sequence is
    returned."""
    return "".join(map(string.strip,
		       data.split(">")[1].split("\n")[1:]))


def fasta_file_sequence(path):
    return fasta_sequence(open(path).read())


def relpath_wo_ext(path):
    return os.path.splitext(os.path.basename(path))[0]


def overlap_at_p(recs, i):
    "Does recs[i] overlap with recs[i+1]? Last record never overlaps."
    return (i<len(recs)-1) and recs[i][VHY_STOP] > recs[i+1][VHY_START]


def overlap_p(recs):
    for i in range(len(recs)-1):
	if overlap_at_p(recs, i):
	    return True
    return False


def pprint_rec(rec, pos_wid=6, pr_wid=4, pr_len_wid=3):
    start, stop, probe, length, ident, pr_len = rec
    parms = (pos_wid, start, pos_wid, stop,
	     pr_wid, repr(probe),
	     length, ident,
	     pr_len_wid, pr_len)
    return "(%*d, %*d, %*s, %3d, %3d, %*d)" % parms


def pprint_recs(recs):
    # TODO: inspect the records and ajust the padding
    strs = []
    for i, r in enumerate(recs):
	recstr = pprint_rec(r)
	if overlap_at_p(recs, i):
	    recstr += " # overlap with next record"
	strs.append(recstr)
    return strs


def probe_name(rec):
    "return the 'canonical', positive probe name"
    return rec[VHY_PROBE].strip("+-")


def build_section_conent(recs, species_name):
    recs.sort()
    warn = overlap_p(recs) and "# WARNING: overlapping hits\n" or ""
    head = warn + "> " + species_name
    body = "\n".join(pprint_recs(recs)) + "\n\n"
    return head + "\n" + body


def build_file_content(recs, species_name=""):
    head = FILE_VERSION_TAG + "\n" + FILE_FORMAT_CMT
    body = build_section_conent(recs, species_name)
    return head + "\n" + body


def build_multi_file_content(sections):
    head = FILE_VERSION_TAG + "\n" + FILE_FORMAT_CMT
    body = "\n".join([build_section_conent(*s) for s in sections])
    return head + "\n" + body
    

def load_vhy(path):
    """Load only the first section of a vhy file.  Return the list of
    tuples and the name of the loaded section"""
    head = open(path).readline().strip()
    if not head == FILE_VERSION_TAG:
	raise Exception("File format not supported")
    # this is tricky since we made the ">" optional...
    recs = []
    name = ""
    for line in open(path).readlines()[1:]:
	if line.startswith("("):
	    # TODO: proper parsing would be safer
	    recs.append(eval(line))
	elif line.startswith(">"):
	    if recs:
		return recs, name
	    else:
		name = line[1:].strip()
    return recs, name


def load_multi_vhy(path):
    """Load the list of parsed sections from a vhy file."""
    head = open(path).readline().strip()
    if not head == FILE_VERSION_TAG:
	raise Exception("File format not supported")

    sections = []
    recs = []
    name = ""
    for line in open(path).readlines()[1:]:
	if line.startswith("("):
	    # TODO: proper parsing would be safer
	    recs.append(eval(line))
	elif line.startswith(">"):
	    if recs:
		sections.append((recs, name))
	    name = line[1:].strip()
	    recs = []
    sections.append((recs, name))
    return sections
