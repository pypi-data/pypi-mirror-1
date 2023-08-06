# ProDaMa: an open source Python library to generate protein structure datasets
#
# ver 1.1 - 2009
#
# IASC group at DIEE - University of Cagliari, P.zza D'Armi, I-09123, Cagliari, Italy
#
# released under the terms of the GNU GPL
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the
#
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.

"""
To perform search by homology sequence
"""

from ProDaMa.services.PDBClient import *
from ProDaMa.services.PSIBlast import callPSIBlast


class SimilaritySearchEngine(object):
    """
    Performs search by homology sequence.
    """
        
    def PSIBlast(self, sequence, ecutoff, iterations):
        """
        Performs a PSI-BLAST homology search
        
        arguments:
            sequence: the target sequence
            
            ecutoff: the E-value 
            
            iterations: the number of PSI-BLAST iterations
        
        return:
            a list of protein identifiers in the form of tuples (structure, chain).
        """
        return callPSIBlast(sequence,ecutoff,iterations)
    
    def FASTA(self, sequence, ecutoff):
        """
        Performs a FASTA homology search.
        
        arguments:
            sequence: the target sequence 
            
            ecutoff: the E-value 
        
        return:
            a list of protein identifiers in the form of tuples  (structure, chain).
        """
        return [(chain_id.split(':')[0],'_ABCDEFGHIJKLMNOPQRSTUVWXYZ'[int(chain_id.split(':')[1])]) for chain_id in PDBClient().fastaQuery(sequence, ecutoff)]