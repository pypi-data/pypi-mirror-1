# ProDaMa: an open source Python library to generate protein structure datasets
#
# ver. 1.0 - 2009
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
Defines the clients related to the used Protein Data Bank web services.
"""


from suds.client import Client
from serviceExceptions import SOAPException

from soaplib.client import make_service_client
from soaplib.service import soapmethod
from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.serializers.primitive import String


class KSPDBService(SimpleWSGISoapApp):

    @soapmethod(String, String, _returns=String,
                _outVariableName='getKabschSanderReturn')
    def getKabschSander(self, pdbid, chainID):
        pass


class PDBClient(object):
    """
    This class defines the clients used for invoking the PDB web services.
    """

    def __init__(self):
        self.client=Client('http://www.pdb.org/pdb/services/pdbws?wsdl')



    def fastaQuery(self, sequence, ecutoff):
        """
        Performs a FASTA query.
        
        arguments:
            sequence: a target sequence
            
            ecutoff: the E-value
            
        return:
            the FASTA response
        """
        try:
            return self.client.service.fastaQuery(sequence,ecutoff).fastaQueryReturn
        except:
            raise SOAPException


    def getSequenceForStructureAndChain(self, str_id,chain_id):
        """
        Retrieves the amino acidic sequence for a given chain.
        
        arguments:
            str_id: a protein structure identifier
            
            chain_id: a chain identifier
            
        return:
            the primary sequence
        
        """
        try:
            return str(self.client.service.getSequenceForStructureAndChain(str_id,chain_id))
        except:
            raise SOAPException


    def getKabschSander(self,str_id,chain_id):
        """
        Retrieves the secondary structure for a given chain.
        
        arguments:
            str_id: a protein structure identifier
            
            chain_id: a chain identifier
            
        return:
            the secondary structure
        """
        try:
            #return str(self.client.service.getKabschSander(str_id,chain_id))
            return make_service_client('http://www.pdb.org/pdb/services/pdbws',KSPDBService()).getKabschSander(str_id, chain_id)
        except:
            raise SOAPException


    def getChains(self, str_id):
        """
        Retrieves the chain identifiers for a given structure.
        
        arguments:
            str_id: a protein structure identifier
            
        returns:
            the chain identifiers
        """
        try:
            return self.client.service.getChains(str_id).getChainsReturn
        except:
            raise SOAPException

    def getObsoletePdbIds(self):
        """
        Retrieves the protein identifiers of the obsolete structures
        
        return:
            the protein identifiers
        """
        try:
            return self.client.service.getObsoletePdbIds().getObsoletePdbIdsReturn
        except:
            raise SOAPException

    def getCurrentPdbIds(self):
        """
        Retrieves the PDB Identifiers (aka PDB IDs) that are "current" structures - not obsolete, models, etc.
        """
        try:
            return self.client.service.getCurrentPdbIds().getCurrentPdbIdsReturn
        except:
            raise SOAPException

