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
Defines the chain of a protein.
"""

from math import sqrt
from string import maketrans

class Chain(object):


    def __init__(self, str_id = None, chain_id  = None, sequence  = None, s_structure  = None, Sec_Struc  = None,
                 Helix = None, ii3 = None, ii5 = None, Beta = None, B_bridge = None, Para_Hb = None, Anti_Hb = None,
                 Amino_Acids = None, T_non_Std = None, Miss_BB = None, Miss_SC = None, only_Ca = None, UNK = None,
                 CYSS = None, Break = None, Nucl_Acids = None, Substrate = None, Water_Mols = None):
                     
        self.str_id = str_id
        self.chain_id  = chain_id
        self.sequence  = sequence
        self.s_structure  = s_structure
        self.Sec_Struc  = Sec_Struc
        self.Helix = Helix
        self.ii3 = ii3
        self.ii5 = ii5
        self.Beta = Beta
        self.B_bridge = B_bridge
        self.Para_Hb = Para_Hb
        self.Anti_Hb = Anti_Hb
        self.Amino_Acids = Amino_Acids
        self.T_non_Std = T_non_Std
        self.Miss_BB = Miss_BB
        self.Miss_SC = Miss_SC
        self.only_Ca = only_Ca
        self.UNK = UNK
        self.CYSS = CYSS
        self.Break = Break
        self.Nucl_Acids = Nucl_Acids
        self.Substrate = Substrate
        self.Water_Mols = Water_Mols
        


    def __getHelix3(self):
        return self.helix3

    def __setHelix3(self, data):
        self.helix3 = data

    def __getHelix5(self):
        return self.helix5

    def __setHelix5(self, data):
        self.helix5 = data

    ii3 = property(__getHelix3, __setHelix3)
    ii5 = property(__getHelix5, __setHelix5)


    def length(self):
        """
        Returns the length of a chain (number of amino acids).
        """
        return len(self.sequence)

    def __translateSequence(self,sequence,alphabet):
        return sequence.translate(maketrans('ACDEFGHIKLMNPQRSTVWY', {'che':'LSAARLBLBLSMIMBHHLRR', 'fun':'HOMMHOPHPHHOHOPOOHHO', 'hyd':'OIIIOIIOIOOIOIIIIOOI'}[alphabet]))


    def sequenceComposition(self, alphabet='iupac'):
        """
        Analyzes the composition of the primary structure according to a specific alphabet. By default the IUPAC protein alphabet is used.

        arguments:
            alphabet: 'che ' for the chemical alphabet, 'fun' for the functional alphabet, 'hyd' for the hydrophobic alphabet.

        return:
            a dictionary with keys the alphabet symbols and value the corresponding frequency
        """
        alphabets={'iupac':list('ACDEFGHIKLMNPQRSTVWY'),'che':list('ABHILMSR'),'fun':list('HMPO'),'hyd':list('OI')}
        translated_sequence = alphabet=='iupac' and self.sequence or self.__translateSequence(self.sequence,alphabet)
        return dict( [(symbol, translated_sequence.count(symbol)/float(self.length())) for symbol in alphabets[alphabet] ])

    def structureComposition(self):
        """
        Analyzes the composition of the secondary structure. For each possible conformation of the secondary structure calculates:  i) the occurrences of the conformation in the secondary structure, ii) the average length of the regions related to the conformation, and iii) the corresponding standard deviation.

        return:
            a dictionary with keys the three possibles conformation of the secondary structure ('H' for alpha-helices, 'E' for 'beta-strands', and 'C' for coils) and values
            a tuple with the above values.
        """
        composition={}
        for conformation in ['H','E','C']:
            composition[conformation]=self.__analyzeConformation(conformation)
        return composition

    def __regions(self, conformation):
        """
        Analyzes the secondary structure of a protein to get the regions associated to a given secondary structure conformation.

        arguments:
            conformation: a possible conformation of the secondary structure: 'H' for alpha-helices, 'E' for beta-strands, and 'C' for coils

        return:
            a list of regions of the given secondary structure conformation
        """
        s_structure=''.join(self.DSSP2HEC())
        ss_filtered={'H':s_structure.replace('C',' ').replace('E',' '),
                         'C':s_structure.replace('H',' ').replace('E',' '),
                         'E':s_structure.replace('C',' ').replace('H',' ')}[conformation]
        return [ss_region for ss_region in ss_filtered.split(' ') if ss_region]

    def __analyzeConformation(self, conformation):
        """
        Calculates some statistics on the secondary structure for a specific conformation.

        arguments:
            conformation: a possible conformation of the secondary structure: 'H' for alpha-helices, 'E' for beta-strands, and 'C' for coils

        return:
            for a given conformation of the secondary structure returns a tuple with three parameters: i) occurrences of the conformation, ii) average length of the regions for the specific conformation anaylzed, and iii) the corresponding standard deviation.
        """
        regions = self.__regions(conformation)
        sizes = [len(region) for region in regions]
        avg = len(sizes)!=0 and sum(sizes)/float(len(sizes)) or 0
        std = len(sizes)!=0 and sqrt(sum([pow(i-avg,2) for i in sizes])/len(sizes)) or 0
        return (sum(sizes),avg,std)

    def getStructureRegionSizes(self):
        region_sizes = {}
        for conformation in ['H','E','C']:
            region_sizes[conformation] = [len(region) for region in self.__regions(conformation)]
        return region_sizes

    def DSSP2HEC(self):
        """
        Encodes the DSSP secondary structure of a protein with three symbols.

        return:
            a three symbols encoding of the secondary structure of the protein.
        """
        s_strucure = []
        for i in self.s_structure:
            if i in ['G','H','I']: s_strucure.append('H')
            elif i in ['B','E']: s_strucure.append('E')
            else: s_strucure.append('C')
        return s_strucure