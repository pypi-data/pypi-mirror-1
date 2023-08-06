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
To search for membrane proteins.
"""

from ProDaMa.model.dbSession import *

class MembraneProtein(object):
    """
    This class provides methods for analysing and searching for membrane proteins in the local database according to a given constraint. 
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
        
    def lookForMP(self, disposition = None):
        """
        Looks for membrane proteins (MP). If a disposition value is specified looks for MP that meet this constraint.

        arguments:
            disposition: a possible disposition value ('Transmembrane' or 'TM Monotopic')

        return:
            a list of protein identifiers in the form of tuples (structure, chain).
        """
        mpData = {True:Session.query(MPData),
                 False:Session.query(MPData).filter_by(disposition = disposition)}[disposition == None].all()    
        return self.__ids and [(mp.str_id, mp.chain_id) for mp in mpData if (mp.str_id, mp.chain_id) in self.__ids] or [(mp.str_id, mp.chain_id) for mp in mpData]
    
    def lookForTMSegments(self,  **range):
        """
        Looks for transmembrane proteins (TM) with a number of TM segments smaller than a minimum value or bigger than a maximum value.  If minimum and maximum values are provided it looks for TM proteins with a number of TM segments between an lower and an upper limit.  
        
        arguments:
            **range: keys 'MIN' and 'MAX'

        return:
            a list of protein identifiers in the form of tuples (structure, chain).
        """    
        mpData = {False:self.__ids and [mp for mp in Session.query(MPData).all() if (mp.str_id, mp.chain_id) in self.__ids],True:Session.query(MPData).all()}[self.__ids == None]
        if range.has_key('MIN'):
            mpData = [mp for mp in mpData if int(mp.nb_segments) >= range['MIN']]
        if range.has_key('MAX'):
            mpData = [mp for mp in mpData if int(mp.nb_segments)<=range['MAX']]
        return [(mp.str_id,mp.chain_id) for mp in mpData]
    
    def lookForTMTopology(self, topology=None):
        """
        Looks for transmembrane proteins (TM) that meet a given constraint on their topology.

        arguments:
            topology: a possible TM topology ('alpha helical' or 'beta barrel')

        return:
            a list of protein identifiers in the form of tuples (structure, chain).
        """    
        mpData={True:Session.query(MPData),
                False:Session.query(MPData).filter_by(topology = topology)}[topology == None].all() 
        return self.__ids and [(mp.str_id,mp.chain_id) for mp in mpData if (mp.str_id,mp.chain_id) in self.__ids] or [(mp.str_id,mp.chain_id) for mp in mpData]
