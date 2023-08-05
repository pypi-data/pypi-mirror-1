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

import os
import sys


#############################################################
#           A L I G N M E N T   A L G O R I T H M
#############################################################

def find_hits(probeSeq, genRef, minRate):
    """ Find the best hits of a nucleotide sequence on a reference 
    genomes. Return the list of the edition distance and the ending 
    index of each best hits. Take a nucleotide sequence, a ref. genome 
    and the minimal rate of error as parameter.
    """
    # Define the treshhold for the hits found
    THRESHOLD = len(probeSeq)-(minRate*len(probeSeq))    
    
    matrix = range(len(probeSeq)+1)
    indices = range(len(probeSeq))
    findHit = False
    
    hits = [] 
    
    # Find the best hits of the sequence on the genome
    for i in range(len(genRef)):
        prev = matrix[0]
        for j in indices:
            temp = matrix[j+1]
            if probeSeq[j] == genRef[i]:
                matrix[j+1] = prev
            else:
                smallest = prev 
                if temp < smallest:
                    smallest = temp
                elif matrix[j] < smallest:
                    smallest = matrix[j]
                matrix[j+1] = smallest + 1
            prev = temp
        
        # Kept the hit only if it's lower then the treshold
        if temp <= THRESHOLD:
            if matrix[len(probeSeq)] > temp and findHit == False:
                hits.append((temp, i))
                findHit = True
            elif matrix[len(probeSeq)] <= temp:
                findHit = False
    
    return hits

    
# Stolen from vhybridize
def fasta_body(filename, block=1):
    "for nucleotides fasta files"
    lines = open(filename).read().split(">")[block].split("\n")[1:]
    body = "".join(map(lambda l:l.strip(), lines))
    return body


# Self test
if __name__ == "__main__":
##    DIR = "/home/masf30087900/Stage en Bioinformatique/UQAM/Projets Python/pipviewer/examples/m_files-beta7"
##    
##    genomeFile = "/home/masf30087900/Stage en Bioinformatique/UQAM/Projets Python/pipviewer/examples/plastids-fixed/Arabidopsis_thaliana.fas"
##    genSeq = fasta_body(genomeFile)
##
##    for file in os.listdir(DIR):
##        print "file is", file
##        filename = os.path.join(DIR, file)
##        probeSeq = fasta_body(filename)
##        hits = find_hits(probeSeq, genSeq, 0.7)
##        for dist, pos in hits:
##            print "dist = " + str(dist) + ", pos = " + str(pos)
    hits = find_hits("AAA", "AGTCCCGTAAAAACGGTTTCCCAACTTTTTT", 0.6)
    for dist, pos in hits:
        print "dist = " + str(dist) + ", pos = " + str(pos)
