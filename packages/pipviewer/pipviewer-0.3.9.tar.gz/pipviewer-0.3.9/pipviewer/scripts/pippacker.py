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
import pipviewer.pselfiles as PSF

from pipviewer import __version__

def parse_args():
    desc = ("Converts a multiple alignment into a form usable by pipviewer."
	    "This software is part of the pipviewer %s package."
            % __version__)
    parser = OptionParser(usage="%prog [options] ALIGN OUTFILE",
                          version="%prog " + __version__,
			  description=desc)

    parser.add_option("-f", "--format",
                      default=None,
                      dest="format",
                      help=("aligment format: 'pip' or 'clustal';"
                            " default is to auto detect"))

    opt, args = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
        sys.exit(1)
    return opt, args


def main():
    opt, args = parse_args()
    align, outpath = args

    fmt_h = dict(txt="pip",
                 aln="clustal")

    importer_h = dict(pip=PSF.import_multipipmaker_file,
                      clustal=PSF.import_clustalw_file)

    if not opt.format:
        ext = os.path.splitext(align)[1][1:]
        if not fmt_h.has_key(ext):
            print "Failed to detect the alignement format."
            print "Try with --format"
            sys.exit(1)
        opt.format = fmt_h[ext]

    mapping = importer_h[opt.format](align)
    PSF.save_mapping(mapping, outpath)


if __name__ == "__main__":
    main()
    
