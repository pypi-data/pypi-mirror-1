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


#############################################################
#            I M P O R T I N G   M O D U L E S
#############################################################

import pselfiles as PSF
import urllib
import os
import sys
import re


#############################################################
#              G L O B A L   C O N S T A N T S
#############################################################

CACHE_NAME = "psel-cache"
WINDOWS = "win"

# where to get the genomes when we have only the id
REFSEQ_URL= ("http://www.ncbi.nlm.nih.gov/entrez/viewer.fcgi?db=nucleotide"
             "&qty=1&c_start=1&val=%(refseqid)s&dopt=%(format)s"
             "&dispmax=5&sendto=t")

#############################################################
#                  E X C E P T I O N S
#############################################################

class URLError(Exception):
    pass

class FastaFileError(Exception):
    pass

#############################################################
#                I / O   A N D   N E T
#############################################################

def remove_dups(lst):
    """ Remove duplicates in a list.  Only the first copy is kept.  A
    new list is returned, the original copy is not modified. 
    """
    seen = {}
    def new_p(elt):
        val = seen.get(elt, True)
        seen[elt] = False
        return val
    return filter(lambda x:new_p(x), lst)


def slice_fas(data, width=70):
    """ Slice a string so that no line is longer than width.  Nothing
    fancy like word boundary checking so only use it for genomic
    sequences. 
    """
    return filter(lambda x:x, map(lambda i:data[i*width:(i+1)*width], 
                range(len(data)/width+1)))


def download_genome(refseqid, format="fasta"):
    """ Download the genome from NCBI.  format can be 'gb' for GenBank
    for 'fasta' for FASTA.  Since the complete genome is returned as a
    string, this function if not good for large genomes.
    """
    data = urllib.urlopen(REFSEQ_URL%vars()).read()
    return data
    

def genome_cache_dir():
    """ Returns where the genome files should be stored on local disk.
    None means that no suitable cache can be found (this is bad).
    """
    # FIXME: This should be loaded from a config file.  Typically
    # multiple users should be able to share a single genome cache.
    path = ""
    if os.environ.has_key("HOME"):
         path = os.path.join(os.environ["HOME"], CACHE_NAME)
    elif os.environ.has_key("HOMEPATH"):
        path = os.path.join(os.environ["HOMEPATH"], CACHE_NAME)
    else:
      raise Exception("no HOME defined")
    
    if not os.path.isdir(path):   
        try:
            os.mkdir(path)
        except OSError:
            return None
    return path
    
 
def genome_file(mapping, idx, format="fasta", download=False):
    """ Return the path of a file containing the genome of mapping[SPECIES][idx] 
    or None if the genome is not available. If download is True and if the 
    refseq id is in the mapping, the genome will be downloaded to localdisk.
    """
    rsid = mapping[PSF.REFSEQ_IDS].get(idx)
    if rsid:
        path = os.path.join(genome_cache_dir(), rsid + "." + format)
        if os.path.isfile(path):
            return path
        elif download:
            data = download_genome(rsid, format)
            if not data.strip():
                raise URLError("Error! BadURL.")
            open(path, "w").write(data)
            return path


def ref_genome_annotations(refGenomeFile, genomeLength):
    """ Return the annoations of the reference genome included in the mapping. 
    Take the reference genome file (genbank) and the reference genome length
    as parameters.
    """
    DIRECT = '+'
    COMPLEMENT = '-'
    
    annotationsLines = []
    anotBlock = False
    
    # Get each line in the file
    for line in open(refGenomeFile):
        line.replace("\r", "")
        if line.startswith("FEATURES"):
            anotBlock = True
        elif line.startswith("ORIGIN"):
            anotBlock = False
        if anotBlock :
            annotationsLines.append(line)
    
    annotations = []
    strandType = ''
    
    # Parse each line and get the genes annotations
    for i in range(len(annotationsLines)):
        stripLine = annotationsLines[i].strip()
        if stripLine.startswith("CDS") or stripLine.startswith("tRNA") \
                or stripLine.startswith("rRNA"):
            j = 1
            while not annotationsLines[i+j].strip().startswith("/gene") \
                    and not annotationsLines[i+j].strip().startswith("/locus_tag") \
                    and not annotationsLines[i+j].strip().startswith("/note"):
                j = j+1
            geneName = annotationsLines[i+j].split("\"")[1]
            start = re.findall(r"(\d+)\.\.\d+", annotationsLines[i])
            stop = re.findall(r"\d+\.\.(\d+)", annotationsLines[i])
            
            # Get the strand type
            if re.search(r"complement", annotationsLines[i]):
                strandType = COMPLEMENT
            else:
                strandType = DIRECT
           
            valide = True
            for pos in stop:
                if int(pos) > genomeLength:
                    valide = False
            if valide:
                for k in range(len(start)):
                    annotations.append([geneName, int(start[k]), int(stop[k]), strandType])

    return annotations
    
    
def adjust_annotations_on_align(annotations, refGenomeAlign):
    """ Return which nucleotide on the align genome is mapped to refPos
    on the reference genome. Take the ref. genes annotations and the ref. 
    genome sequence as parameters.
    """
    alignAnnotations = []
        
    for geneName, refStart, refStop, strandType in annotations:
        alignStart = 0
        while refStart > 1:
            if refGenomeAlign[alignStart] != '-':
                refStart = refStart-1
            alignStart = alignStart+1
        
        alignStop = 0
        while refStop > 1:
            if refGenomeAlign[alignStop] != '-':
                refStop = refStop-1
            alignStop = alignStop+1 
            
        alignAnnotations.append((geneName, alignStart, alignStop, strandType))     
        
    return alignAnnotations
    

# little self test
if __name__ == "__main__":
    print genome_cache_dir()
    
