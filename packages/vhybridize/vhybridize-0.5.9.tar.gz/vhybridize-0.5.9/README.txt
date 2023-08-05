

Virtual Hybridization
=====================

This package contains Virtual Hybridization tools.  Virtual
Hybridization uses sets of short probes to generate datasets for
comparative genomics: given a DNA sequence and a set of probes, the
typical output will give a sequence of oriented probe hits along the
DNA sequence. Other tools are supplied to allow simple manipulations
such as format conversion and extraction of permutations.


Requirements
------------

To use this package you will need Python 2.4 or later.  

To compute the position of probes you will need BLAST and optionally
needle from Emboss.  Those programs must be in your search path.

Minimal usage of the shell is done.  You should be able to run it on a
Posix system (including Mac OSX) and on MS Windows on top of Cygwin.
That being said, the software was only fully tested on Debian
GNU/Linux 4.0 (Etch).

On a Debian based system, you can install those dependencies with:

  apt-get install python-qt3 python-qt3-gl python-qtext python-opengl


Installation
------------

With easy_install:

  easy_install vhybridize

Alternative manual installation:

  tar -zxvf vhybridize-X.Y.Z.tar.gz
  cd vhybridize-X.Y.Z
  python setup.py install

Where X.Y.Z is a version number.

If you are not root or if you don't want to install the system
globally, you should use a
http://pypi.python.org/pypi/virtualenv[virtualenv].


Input files
-----------

Basic Virtual Hybridization requires two types of input
files:

   * A set of probes.  Example: `chloroplasts-probes-1.0.fas`
   * A DNA sequence.  Examples: `NC_000932.fas`, `NC_004766.fas`

The set of probes must be in multi-fasta format and there should be
one mono-fasta file for each DNA sequence of interest.


Basic Virtual Hybridization
---------------------------

The following command:

  vhybridize -p chloroplasts-probes-1.0.fas NC_000932.fas 

will produce the file

  output/nc_000932.vhy

Virtual Hybridization of the same set of probes with a second DNA
sequence, such as nc_004766.fas, will produce a different probe order,
such as nc_004766.vhy.  When only the probe order is wanted, output
files can be stripped of all meta-information with the command
vhy-to-vhx:

  vhy-to-vhx nc_000932.vhy nc_004766.vhy > foo.vhx

The file foo.vhx can then be fed to software that compare gene order,
such as those available at http://cgl.bioinfo.uqam.ca/tools/form .


Documentation
-------------

See the `docs` directory for more documentation.


Acknowledgments
---------------

This original development of this software was done at the
Comparative Genomics Laboratory at UQAM:

  http://cgl.bioinfo.uqam.ca 
