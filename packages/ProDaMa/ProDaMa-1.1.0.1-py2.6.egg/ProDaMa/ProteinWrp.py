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
To update the local database.
"""

from ProDaMa.model.dbSession import *
from ProDaMa.PDBWrp import *
from ProDaMa.EBIWrp import *
from ProDaMa.MPDataWrp import *
from ProDaMa.services import PDBFinderWrp

class ProteinWrp(object):
    """
    This class should be used to update the local database with protein information retrieved from remote sources.
    """

    def getProtein(self, str_id):
        """
        For a given a structure protein identifier retrieves its related information from different Bioinformatics sources. In particular particular: i) chains from the Protein Data Bank (PDB), ii) information about protein CATH and SCOP classification from the European Bioinformatics Institute (EBI), iii) other protein data from the PDBFINDER database, and iv) information about membrane protein topologies from the MPTopo database.

        arguments:
            str_id : a structure protein identifier
    
        return:
            a Protein object
        """
        protein = Protein()
        protein.str_id = str_id 
        PDBFinderWrp.checkForChanges()
        pdb_finder_data = PDBFinderWrp.getStructureData(str_id) 
        if pdb_finder_data:
            for field,value in pdb_finder_data.items(): setattr(protein, field, value or None)
        scop_statistics = EBIWrp().getSCOPClassification(str_id)
        scop_statistics and protein.scopClassification.append(SCOPProteinData(scop_statistics))
        cath_statistics = EBIWrp().getCATHClassification(str_id)
        cath_statistics and protein.cathClassification.append(CATHProteinData(cath_statistics))
        pdb_finder_data = PDBFinderWrp.getChainData(str_id)
        pdbwrp = PDBWrp()
        for chain_id in pdbwrp.getChains(str_id):
            chain = Chain() 
            chain.chain_id = chain_id
            chain.sequence = pdbwrp.getSequence(str_id,chain_id)
            chain.s_structure = pdbwrp.getStructure(str_id,chain_id)
            if pdb_finder_data:
                for field,value in pdb_finder_data[chain_id].items(): 
                    setattr(chain,field,value or None)
            TM = MPDataWrp().getData(chain.sequence)
            if TM:
                chain.mpData.append(TM)
            protein.chains.append(chain) 
        return protein

    def store(self, protein):
        """
        Stores in the database the data associated with a protein.
    
        arguments:
            protein: a Protein object
        """
        try:
            Session.add(protein)
            Session.commit()
        except: raise
    
    def remove(self, str_id):
        """
        Removes from the database the data related to a given protein identifier.

        arguments:
            str_id : a structure protein identifier
        """
        try:
            Session.execute(protein_table.delete().where(protein_table.c.str_id==str_id))  
            Session.commit()                                                               
        except:
            raise

    def removeObsoletes(self):
        """
        Removes the obsolete proteins from the database.
        """
        pdbWrp=PDBWrp()
        for str_id in pdbWrp.getObsoleteIds(): self.remove(str_id)
    
    def update(self):
        """
        The update process consists of three steps: i) the first step consists to look for obsolete proteins in the PDB and remove the corresponding data from the local database, ii) the second step consists to look for new proteins in the PDB, and iii) the third step consists to retrieve and store information associated with these proteins
        """
        #self.removeObsoletes()
        pdbWrp = PDBWrp()
        for str_id in pdbWrp.lookForChanges():
            self.remove(str_id)
        proteins_in_db = [str_id[0] for str_id in Session.query(Protein.str_id).all()]
        proteins_to_load = [str_id for str_id in pdbWrp.getIds() if str_id not in proteins_in_db]
        for str_id in proteins_to_load:
          try:
            self.store(self.getProtein(str_id))
          except:
            pass
