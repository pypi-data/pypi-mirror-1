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
To search for SCOP classified proteins.
"""

from ProDaMa.model.dbSession import *

class SCOP(object):
    """
    This class provides search methods applied to the local database for selecting proteins according to a given constraint on their SCOP classification.
    """
    def __init__(self, protein_ids = None):
        """
        Initializes the set of proteins to be analyzed.
            
        arguments:            
            protein_ids: a list of protein identifiers in the form of tuples (structure, chain). By default (protein_ids=None) the set of proteins to be analyzed coincides with all proteins in the database.             
        """
        self.__ids = protein_ids
    
    def setProteinIds(self, protein_ids):
        """
        Permits to change the set of proteins to be analyzed.
            
        arguments:            
            protein_ids: a list of protein identifiers in the form of tuples (structure, chain).
        """
        self.__ids = protein_ids
        
    def __lookFor(self, level, constraint, like=False):
        """
        Looks for proteins that meet a given constraint on a specific hierarchical classification level. 
            
        arguments:
            level: a hierarchical classification level 
                
            constraint: a possible classification for the level
            
        return:
            a list of protein identifiers in the form of tuples (structure, chain).  
        """
	exec(like and 'scopProteinData = Session.query(SCOPProteinData).filter(SCOPProteinData.%s.like("%s")).all()'%(level,'%'+constraint+'%') or 'scopProteinData = Session.query(SCOPProteinData).filter_by(%s=constraint).all()'%level)
        str_ids=[protein_data.str_id for protein_data in scopProteinData]
        found_chains=[(chain.str_id,chain.chain_id) for chain in Session.query(Chain).filter(Chain.str_id.in_(str_ids)).all()]
        return self.__ids and [protein_id for protein_id in self.__ids if protein_id in found_chains] or found_chains

 
    def lookForClassification(self,  **classification):
        """
        Looks for proteins that meet a given constraint on the SCOP classification.
        
        arguments:
           **classification: a SCOP classification (keys: 'Class', 'fold', 'family', 'superfamily'). 
            
        return:
            a list of protein identifiers in the form of tuples (structure, chain).
        """	
        protein_ids = set(self.__ids)
        for level, constraint in classification.items():
            try:
                exec ('protein_ids&=set(self._SCOP__lookFor(level,constraint))')
            except:
                return []
        return list(protein_ids)
