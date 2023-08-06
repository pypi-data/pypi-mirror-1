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
To perform search by identity sequence.
"""

from ProDaMa.services.PISCESInterface import cullFromPDB
from ProDaMa.model.dbSession import *

class IdentitySearchEngine(object):
    """
    Performs search by identity sequence.
    """
    
    def __init__(self, protein_ids = None):
        """
        Initializes the set of proteins to be analyzed.
            
        arguments:            
            protein_ids: a list of protein identifiers in the form of tuples (structure, chain). By default (protein_ids=None) all proteins are examined. 
            
        """
        self.__ids= protein_ids

    def setProteinIds(self, protein_ids = None):
        """
        Initializes the set of proteins to be analyzed.

        arguments:
            protein_ids: a list of protein identifiers in the form of tuples (structure, chain). By default (protein_ids=None) all proteins are examined.

        """
        self.__ids= protein_ids


    
    def sequencesCullFromPDB(self, **parameters):
        """
        Culls (using PISCES) sets of protein sequences from the overall local database or from a specified subset according to sequence identity and structural criteria. 
            
        arguments:
            **parameters: the PISCES parameters. By default the following parameters are used:
                    'MAX_percentage_identity'=25,
                    'MIN_resolution'=0.0,
                    'MAX_resolution'=2.5,
                    'MIN_chain_length'=20,
                    'MAX_chain_length'=10000,
                    'RFactor'=0.3,
                    'skip_non_x'=True, 
                    'skip_CA_only'=True
                    
        return:
            a list of protein identifiers in the form of tuples (structure, chain).
        """
        protein_ids = self.__ids and ["%s%s"%protein_id for protein_id in self.__ids] or ["%s%s"%(chain.str_id,chain.chain_id) for chain in Session.query(Chain).all()]
        interface_parameters=','.join(["%s=parameters['%s']"%(parameter, parameter) for parameter in parameters])
        exec ("culled=cullFromPDB(protein_ids,%s)"%interface_parameters)
        return [(protein_id[:4],protein_id[-1]) for protein_id in culled]
        
    
