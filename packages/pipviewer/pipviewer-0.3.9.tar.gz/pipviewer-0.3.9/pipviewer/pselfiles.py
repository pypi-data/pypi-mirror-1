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


""" Managment of the input files """

#############################################################
#            I M P O R T I N G   M O D U L E S
#############################################################

# our files are just pickled dicts
from cPickle import load, dump

import os
from copy import copy
from time import time
import re
import random


#############################################################
#              G L O B A L   C O N S T A N T S
#############################################################

# By design, to easy manipulation by external scripts, the input files
# are just pickled dicts.  We will do out best to keep the format as
# stable as possible so you can free play with its content directly
# without using an opaque interface.  Internally, we reffer to the
# content of loaded file as a "mapping".

# The mapping features a multiple alignment and "annotations" on this
# alignment that the user can add.  Those annotations are (start, stop)
# tuples describing regions.  Region can be selected probes,
# break-points, ... (more on this later)

# The description in this file refers to a single version of the file
# format.  If you need to use a legacy file, look at the content of
# this file in a passed release of this software.
FILE_FORMAT_VERSION = 6
VERSION_KEY = "format-version"

# The official extention stands for Probe SELector
FILE_FORMAT_EXT = ".psel"

# The minimal length of the probes's names
NAMES_MIN_LENGTH = 3

#############################################################
#                     K E Y S
#############################################################

# The region types, regions are (start, stop) tuples with the Python
# slice semantic.
PROBES = "probes" # selected probes
BREAKS = "break-points" # low conservation (not really used)
TRASHS = "trash-regions" # good conservation but poor score as a probe
REGION_TYPES = [PROBES, BREAKS, TRASHS]

# The mapping contains a multiple alignment, we need the alignment
# sequence for each species and the species name.  Those will point to
# list of strings
ALIGN = "aligned-sequences"
SPECIES = "species-names"
PROBES_IDS = "probes-ids"
PROBES_IDS_LENGTH = "probes-ids-length"

# To compute the probe scores we need the ref genomes, either refseq
# number or the genome files.  Those keys are optional and will point to
# dict with integers as key.  We use the index of the species in the
# multiples alignment to map to its genome.
REFSEQ_IDS = "ref-seq-ids"
GENES_ANNOTATIONS = "genes-annotations"

# TODO: those are not implemented yet
#GENBANKS   = "genbank-files"
#FASTAS     = "fasta-files"


#############################################################
#                  E X C E P T I O N S
#############################################################

class FileFormatError(Exception):
    pass

class MappingFormatError(Exception):
    pass
    
class InvalidFormatError(Exception):
    pass


#############################################################
#                          I / O
#############################################################

def load_mapping(file):
    """ Return the hashMap containing the alignment data. Take a filename 
    or an opened file as parameter. 
    """
    f = file
    try:
        f.read
    except AttributeError:
        f = open(file)
    
    try:
        mapping = load(f)
    except:
        raise FileFormatError("file isn't loadable by the pickel module")

    if mapping[VERSION_KEY] < FILE_FORMAT_VERSION:
        raise FileFormatError("file format version is deprecated")
    
    if mapping[VERSION_KEY] != FILE_FORMAT_VERSION:
        raise FileFormatError("file format version not supported")

    return mapping
    

def save_mapping(mapping, file):
    """ Save the data contain in the mapping. Take a filename or an opened
    file as parameter (mapping is a dict).
    """
    f = file
    try:
        f.write
    except AttributeError:
        f = open(file, "w")

    # minimal validation
    for k in [ALIGN, SPECIES, REFSEQ_IDS, PROBES_IDS, PROBES, BREAKS, TRASHS, PROBES_IDS_LENGTH]:
        if not mapping.has_key(k):
            raise MappingFormatError("mapping lacks the " + k +" key")

    # we use proto 0 since Windows seems to have problem with the
    # latest proto.
    versionned_mapping = copy(mapping)
    versionned_mapping[VERSION_KEY] = FILE_FORMAT_VERSION

    # for various reasons its a good idea to sort the annotations
    for k in REGION_TYPES:
        versionned_mapping[k].sort()

    dump(versionned_mapping, f, 0)
    

def set_empty_mapping(align, species):
    """ Return the default mapping containing the minimal data witch are the
    species names, the multiple alignment and the probes' name minimal length.
    Take the multiple alignment and the species list as parameters. 
    """
    mapping = { VERSION_KEY:FILE_FORMAT_VERSION,
                ALIGN:align,
                SPECIES:species,
                REFSEQ_IDS:{},
                PROBES_IDS:{},
                PROBES:[],
                BREAKS:[],
                TRASHS:[],
                PROBES_IDS_LENGTH:NAMES_MIN_LENGTH,
                GENES_ANNOTATIONS:[] }
    return mapping


def import_multipipmaker_file(file):
    """ Import a multipipmaker multiple alignement file. The content of 
    the file is read and then converted into a valid mapping.
    """  
    data = open(file).read()
    mapping = mapping_from_multipipmaker(data)
    return mapping


def import_clustalw_file(file):
    """ Import a clustalw multiple alignement file. The content of 
    the file is read and then converted into a valid mapping
    """  
    data = open(file).read()
    mapping = mapping_from_clustalw(data)
    return mapping


def mapping_from_multipipmaker(data):
    """ Convert a multipipmaker multiple alignement into a valid
    mapping. Data is the content of the ASCII produced by multipipmaker.
    At this stage we can't parse the pdf or postscript file.
    """
    # FIXME: will this work on mac ?
    lines = filter(lambda l:l, map(lambda l:l.strip(), data.split("\n")))
    nb_seq, length = map(int, lines[0].split(" "))

    # from nb_seq to end is the align
    align = lines[nb_seq+1:]
    species = lines[1:nb_seq+1]
    
    # Validation of the Pipmaker Format
    if nb_seq != len(align) or len(species) != len(align):
        raise InvalidFormatError("The file is not a valid Pipmaker format")
    
    for line in align:
        if len(line) != length:
            raise InvalidFormatError("The file is not a valid Pipmaker format")
    
    return set_empty_mapping(align, species)


def mapping_from_clustalw(data):
    """ Convert a clustalW multiple alignement into a valid mapping.
    Data is the content of te ASCII produced by clustalW (.aln file).
    """
    lines = [l.replace("\r", "") for l in data.split("\n")]
    if not re.match(r"CLUSTAL (W|X) \(\d\.\d+\)", lines[0]):
        raise InvalidFormatError("The file is not a valid ClustalW format")
    
    # TODO: this parsing will not work on macs
    blocks = []
    cur_block = []
    for l in lines[3:]:
        if l == "":
            blocks.append(cur_block)
            cur_block = []
        else:
            cur_block.append(l)
    
    species = []
    align = []
    for line in blocks[0]:
        if line[0] != " ":
            species.append(line.split()[0])
            align.append(line.split()[1])
    
    nb_seq = len(species)
    
    for i in range(nb_seq):
        j = 1
        while j < len(blocks):
            align[i] = align[i] + blocks[j][i].split()[1]
            j = j+1
    seq_length = len(align[0])
    
    # Validation of the clustal format
    if nb_seq != len(species):
        raise InvalidFormatError("The file is not a valid ClustalW format")
    
    for seq in align:
        if len(seq) != seq_length:
            raise InvalidFormatError("The file is not a valid  Clustal format")
    
    return set_empty_mapping(align, species)

 
#############################################################
#                        U T I L S
#############################################################

def conservation(mapping, pos):
    """ Return a value in [0..1] for the conservation.  pos is a 0
    based position on the multiple alignment.  No bound checking is
    done. Gaps are never considered conserved and we take the
    nucleotide that appears the most, not necessarily the one on the
    ref genome.
    """
    occ = {}
    vals = mapping[ALIGN]
    for s in vals:
        occ[s[pos]] = occ.get(s[pos], 0) + 1
    return 1.0*max([occ.get(n, 0) for n in ["A", "C", "G", "T"]])/len(vals)


def ref_genome_seq(mapping, start, stop):
    """ Return the ref genome sequence between start and stop.
    Position are on the multiple alignment and gaps are trimed.
    """
    return mapping[ALIGN][0][start:stop].replace("-", "")

      
def generate_probe_name(wordLength):
    """ Return a random name compose of a altenate vowel an consomne. Take 
    the name length as parameter.
    """
    VOWEL = "aeiouy"
    CONSOMNE = "qwrtpsdfghjklzxcvbnm"
    
    random.seed(time())
    name = "P"
    for i in range(wordLength):
        if i%2 == 0:
            name = name + random.choice(VOWEL)
        else:
            name = name + random.choice(CONSOMNE)
    
    return name
    
   
def next_probeName(mapping, start, stop):
    """ Generate name for a probe sequence and add it to the mapping. Return
    the modified mapping. Take the unmodified mapping and the starting and
    ending position of the probe sequence as parameters.
    """
    # Define the max limit before updating the name length
    MAX_LIMIT = 5
    
    wordLength = mapping[PROBES_IDS_LENGTH]
    limit = 0
    probeNames = []
    keys = []
    currentKey = (start, stop)
    
    # Generate a probe name
    newName = generate_probe_name(wordLength)
    
    for key in mapping[PROBES_IDS]:
        probeNames.append(mapping[PROBES_IDS][key])
        keys.append(key)
    
    # Return the unmodified mapping if the probe name is already define
    if currentKey in keys:
        return mapping
    
    # Add the probe name to the mapping if it don't exist
    else:
        while newName in probeNames and key != currentKey:
            newName = generate_probe_name(wordLength)
            limit = limit+1
            if limit == MAX_LIMIT:
                wordLength = wordLength+1
        mapping[PROBES_IDS_LENGTH] = wordLength
        mapping[PROBES_IDS][currentKey] = newName
        return mapping
    

# simple self test
if __name__ == "__main__":
    import sys
    load_mapping(sys.argv[1])

    
