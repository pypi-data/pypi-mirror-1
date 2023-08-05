

Pip Viewer
==========

Pipviewer is a visualizer for multiple alignements of genomic
sequences.  It highlights conserved regions and allows basic
anotations.  Its main goal is to find conserved probes for the
construction of gene order data sets.  Selected regions marked as
'probes' can be expoxted to fasta format.  It can also retreive gene
annotations form the NBCI and display this information along the
alignement.

Pipviewer is not an aligner.  You must compute the alignment with
another tool like Clustal or Multi PIP Maker.  

Pipviewer is a Free Software released under the GNU GPL version 3.
See `COPYING.txt` for the details.


Requirements
------------

To use this package you will need :

- Python 2.4 or later
- PyOpenGL 2.0 or later
- PyQt 3.11 or later
- vhybridize 0.5.9 or later


Installation
------------

With easy_install:

  easy_install pipviewer

Alternative manual installation:

  tar -zxvf pipviewer-X.Y.Z.tar.gz
  cd pipviewer-X.Y.Z
  python setup.py install

Where X.Y.Z is a version number.

If you are not root or if you don't want to install the system
globally, you should use a
http://pypi.python.org/pypi/virtualenv[virtualenv].


Quick Start
-----------

Compute a multiple alignment of selected sequences with Multi PIP
Maker and save the result as `foo.txt`.  Convert the format in a
representation that pipviewer can use:

  pippacker foo.txt foo.psel

Display the multiple alignment:

  pipviewer foo.psel

You can now select regions by dragging the mouse over them.  Select a
few regions and mark them as 'probes'.  You can now export those in
fasta format from the _file_ menu.

If you do not have a multiple alignment handy, you use try pipviewer
with the files in the `examples` directory.


Documentation
-------------

See the `docs` directory for more documentation.


Acknowledgments
---------------

This original development of this software was done at the
Comparative Genomics Laboratory at UQAM:

  http://cgl.bioinfo.uqam.ca 
