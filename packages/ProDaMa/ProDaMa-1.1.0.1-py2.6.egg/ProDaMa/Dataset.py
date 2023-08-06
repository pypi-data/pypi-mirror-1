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
Defines a protein dataset.
"""



import datetime
from types import *
from math import sqrt



class Dataset(object):
    """
    This class must be used to represents a protein dataset.
    """

    def __new__(cls, dataset=None):
        from ProDaMa.model.dbSession import Session
        if type(dataset)==str:
            return Session.query(Dataset).filter_by(name = dataset).first()
        else:
            return super(Dataset,cls).__new__(cls)


    def __init__(self, dataset=None):
        """
        Initializes a Dataset object
        
        parameters:
            dataset: the name of a dataset stored in the local database, a list of protein identifiers (structure, chain). If no parameter is passed the dataset is instantiated on the overall database.
            
        """
	from ProDaMa.model.dbSession import Session, Chain
	
        if type(dataset)!=str:
            self.date = datetime.datetime.now()
            self.name = str(self.date)
            self.chains = dataset and [Session.query(Chain).filter_by(str_id=protein_id[0], chain_id=protein_id[1]).first() for protein_id in dataset] or Session.query(Chain).all()
            self.chains_n = len(self.chains)

    def addChains(self, protein_ids):
        """
        Adds a set of protein identifiers to the starting set.
        
        arguments:
            protein_ids: a list of protein identifiers (structure, chain).
        """
        from ProDaMa.model.dbSession import Session, Chain
        to_add= [Session.query(Chain).filter_by(str_id = protein_id[0], chain_id = protein_id[1]).first() for protein_id in protein_ids]
        self.chains = self.chains and self.chains+to_add or to_add

    def removeChains(self, protein_ids):
        """
        Removes a set of chains from the dataset.

        arguments:
            protein_ids: a list of protein identifiers (structure, chain).
        """
        self.chains = [chain for chain in self.chains if (chain.str_id,chain.chain_id) not in protein_ids]

    def getName(self):
        """
        Returns the name of the dataset.
        """
        return self.name

    def size(self):
        """
        The size of the dataset (intended as the number of proteins).
        """
        return len(self.chains)

    def getIds(self):
        """
        Returns a list of the identifiers of the proteins belonging at the dataset.
        """
        return [(chain.str_id,chain.chain_id) for chain in self.chains]
  
    def averageLength(self):
        """
        Calculates the average length of a protein in the dataset.
        """
        return sum([len(chain.sequence) for chain in self.chains])/float(len(self.chains))

    def length(self):
        """
        The overall length of all sequences.
        """
        return sum([len(chain.sequence) for chain in self.chains])


    def lookForSeqLength(self, **range):
        """
        Looks for chains that meet a given constraint on their length.

        arguments:
            **range: keys: 'MIN' (a lower limit) and 'MAX'(an upper limit). If both 'MIN' and 'MAX' are provided, it looks for chains with length ranging between these values, else looks for chains with length smaller than 'MIN' or bigger than 'MAX'.

        return:
            a list of protein identifiers (structure, chain).
        """
        from ProDaMa.model.dbSession import Session, Chain
        chains = self.chains and list(self.chains) or [chain for chain in Session.query(Chain).all()]
        chains = range.has_key('MIN') and [chain for chain in chains if len(chain.sequence)>range['MIN']] or chains
        chains = range.has_key('MAX') and [chain for chain in chains if len(chain.sequence)<range['MAX']] or chains
        return [(chain.str_id,chain.chain_id) for chain in chains]


    def encode(self, accession_number):
        """
        For each protein in the dataset encodes the primary structure according to a given accession number of the AAIndex1.

        arguments:
            accession_number: a valid accession number of the AAIndex1 (http://www.genome.jp/aaindex/)

        return:
            a dictionary with keys the protein identifier and value the sequence encoded.
        """
        from ProDaMa.model.dbSession import Session, AAData
        try:
            aadata = Session.query(AAData).filter_by(accession=accession_number).one()
        except: #bogus accession number
            return None
        encoded_chains = {}
        for chain in self.chains:
            try:
                encoded_chains[(chain.str_id,chain.chain_id)] = [getattr(aadata,amino_acid) for amino_acid in chain.sequence]
            except:
                encoded_chains[(chain.str_id,chain.chain_id)] = None
        return encoded_chains


    def selectChain(self, mode):
	"""
	Looks for single or multi-chain proteins in the dataset.
	
	arguments:
            mode: can take two values: 'single' for single-chain proteins chain or 'multi' for multi-chain proteins.

        returns:
            a list of protein identifiers (structure, chain)
	"""
        return mode == 'single' and self.multiChainProteins(1) or mode == 'multi' and self.multiChainProteins()

    def multiChainProteins(self, nb_of_chains=None):
        """
        Looks for multi-chain proteins in the dataset.

        arguments:
            nb_of_chains: a constraint on the number of chains. By default looks for proteins with two or more chains.

        returns:
            a list of protein identifiers (structure, chain)
        """
        str_ids = [protein_id[0] for protein_id in self.getIds()]
        return nb_of_chains and [protein_id for protein_id in self.getIds() if str_ids.count(protein_id[0])==nb_of_chains] or [protein_id for protein_id in self.getIds() if str_ids.count(protein_id[0])>1]

    def lookForProteinQuality(self, **parameters):
        """
        Looks for proteins that meet a given constraint on their structure quality.

        arguments:
            **parameters:
                    'exp_method': the experimental method used
                    'MIN_res': a lower limit for the resolution
                    'MAX_res': an upper limit for the resolution
                    'MIN_rfactor': a lower limit for the R factor
                    'MAX_rfactor': an upper limit for the R factor
                    'MIN_rfree': a lower limit for the R free
                    'MAN_rfree': an upper limit for the R free

        returns:
            a list of protein identifiers (structure, chain)
        """
        from ProDaMa.model.dbSession import Session, Protein
        proteins = Session.query(Protein).filter(Protein.str_id.in_(set([protein_id[0] for protein_id in self.getIds()]))).all()
        proteins = parameters.has_key('exp_method') and [protein for protein in proteins if protein.Exp_Method==parameters['exp_method']] or proteins
        proteins = parameters.has_key('MIN_res') and [protein for protein in proteins if protein.Resolution>=parameters['MIN_res']] or proteins
        proteins = parameters.has_key('MAX_res') and [protein for protein in proteins if protein.Resolution<=parameters['MAX_res']] or proteins
        proteins = parameters.has_key('MIN_rfactor') and [protein for protein in proteins if protein.R_Factor>=parameters['MIN_rfactor']] or proteins
        proteins = parameters.has_key('MAX_rfactor') and [protein for protein in proteins if protein.R_Factor<=parameters['MAX_rfactor']] or proteins
        proteins = parameters.has_key('MIN_freer') and [protein for protein in proteins if protein.Free_R>=parameters['MIN_freer']] or proteins
        proteins = parameters.has_key('MAX_freer') and [protein for protein in proteins if protein.Free_R<=parameters['MAX_freer']] or proteins

        return [(chain.str_id,chain.chain_id) for chain in self.chains if chain.str_id in [protein.str_id for protein in proteins]]


    def getSequenceStatistics(self, alphabet='iupac'):
        """
        Analyzes the primary structure composition of the proteins in the dataset according to a specific alphabet. By default the IUPAC protein alphabet is used.

        arguments:
            alphabet: 'che ' for the chemical alphabet, 'fun' for the functional alphabet, 'hyd' for the hydrophobic alphabet.

        returns:
            a dictionary with keys the alphabet symbols and value a tuples with the following parameters: i) the relative frequency of the alphabet symbol in the dataset, ii) the average frequency of the alphabet symbol in a sequence of the dataset, and iii) the corresponding standard deviation.
        """
        
        dataset_composition = {}
        chains_length = 0
        for chain in self.chains:
            chains_length+=len(chain.sequence)
            sequence_composition = chain.sequenceComposition(alphabet)
            for symbol, relative_frequency in sequence_composition.items():
                if dataset_composition.has_key(symbol) :
                    dataset_composition[symbol].append((chain.sequence.count(symbol), relative_frequency))
                else:
                    dataset_composition[symbol] = [(chain.sequence.count(symbol), relative_frequency)]
        for symbol in dataset_composition:
            average_frequency=sum([composition[1] for composition in dataset_composition[symbol]])/float(len(dataset_composition[symbol]))
            dataset_composition[symbol]=( sum([composition[0] for composition in dataset_composition[symbol] ])/float(chains_length),
                                                                average_frequency,
                                                                sqrt(sum([pow(composition[1]-average_frequency,2)]) )/float(len(dataset_composition[symbol]))
                                                            )
        return dataset_composition



    def structureComposition(self):
        """
        Analyzes the secondary structure composition of the proteins in the dataset. For each possible conformation of the secondary structure calculates:  i) the relative frequency of the conformation in the secondary structure, ii) the average length of the regions related to the conformation, and iii) the corresponding standard deviation.


        returns:
            a dictionary with keys the three possibles conformation of the secondary structure ('H' for alpha-helices, 'E' for 'beta-strands', and 'C' for coils) and values
            a tuple with the above statistics.
        """
        dataset_regions = {'E':[],'H':[],'C':[]}
        chains_total_length = 0
        for chain in self.chains:
            chains_total_length += len(chain.s_structure)
            chain_regions = chain.getStructureRegionSizes()
            for conformation in chain_regions.keys():
                dataset_regions[conformation]+=chain_regions[conformation]
        structure_composition={}
        for conformation in dataset_regions.keys():
            relative_frequency = sum(dataset_regions[conformation])/float(chains_total_length)
            average_length = sum(dataset_regions[conformation])/float(len(dataset_regions[conformation]))
            standard_deviation = sqrt(sum([pow(size-average_length,2) for size in dataset_regions[conformation]]))/float(len(dataset_regions[conformation]))
            structure_composition[conformation] = (relative_frequency,average_length,standard_deviation)
        return structure_composition


    def lookForStructureComposition(self, label, **frequency):
        """
       Looks for proteins in the dataset that meet a given constraint on the relative frequency of occurrence of a given conformation of the secondary structure.

       arguments:

           label: a possible conformation of the secondary structure: 'H' for alpha-helices, 'E' for beta-strands, and 'C' for coils

           **frequency: the relative frequency of occurrences. Possibile keys are 'MIN', and 'MAX'.

       return:
           a list of protein identifiers
        """
        relative_frequencies = {}
        for chain in self.chains:            
            relative_frequencies[(chain.str_id,chain.chain_id)] = len(chain.s_structure)>0 and chain.structureComposition()[label][0]/float(len(chain.s_structure)) or 0
        valid_chains = frequency.has_key('MIN') and [protein_id for protein_id,relative_frequency in relative_frequencies.items() if relative_frequency >= float(frequency['MIN']) ] or relative_frequencies.keys()
        valid_chains = frequency.has_key('MAX') and [protein_id for protein_id in valid_chains if relative_frequencies[protein_id]<=float(frequency['MAX'])] or valid_chains
        return valid_chains

    def store(self, name, description=None):
	"""
	Stores the dataset in the local database.

	arguments:
    		name: a unambiguous name

                description: database description
	"""

	from ProDaMa.model.dbSession import Session
        self.name = name
        self.description = description or ""
        try:
            Session.add(self)
            Session.commit()
        except:
            #Probably name is already present
            raise


    def remove(self):
	"""
	Removes the memberships of a the dataset with the proteins in the local database.

	"""
	
        from ProDaMa.model.dbSession import Session
        Session.delete(self)
        Session.commit()


    def union(self, dataset):
        """
        Generates a list of protein identifiers from the union of two Dataset.

        arguments:
           dataset: a Dataset object

        return:
            a list of protein identifiers in the form of tuples (structure, chain)
        """
        return list(set(self.getIds()+dataset.getIds()))

    def difference(self, dataset):
        """
        Generates a list of protein identifiers from the difference of two Dataset.

        arguments:
           dataset: a Dataset object

        return:
            a list of protein identifiers in the form of tuples (structure, chain)
        """
        return list(set(self.getIds())-set(dataset.getIds()))


    def intersection(self, dataset):
        """
        Generates a list of protein identifiers from the intersection of two or more Dataset.

        arguments:
           dataset: a Dataset object

        return:
            a list of protein identifiers in the form of tuples (structure, chain)
        """
        return list(set(self.getIds()) & set(dataset.getIds()))

    def lookForCATHClassification(self, **classification):
	"""
	Looks for proteins in the dataset that meet a given constraint on the CATH classification.
	
	arguments:
	    **classification: a CATH classification (keys:  'Class', 'architecture', 'topology', 'homologous').

	return:
	     a list of protein identifiers in the form of tuples (structure, chain).
	"""
	
        from ProDaMa.CATH import CATH
        return CATH(self.getIds()).lookForClassification(**classification)

    def lookForSCOPClassification(self, **classification):
	"""
	Looks for proteins in the dataset that meet a given constraint on the SCOP classification.

	arguments:
		**classification: a SCOP classification (keys: 'Class', 'fold', 'family', 'superfamily'). 
	
	return:
		a list of protein identifiers in the form of tuples (structure, chain).
	"""
        from ProDaMa.SCOP import SCOP
        return SCOP(self.getIds()).lookForClassification(**classification)
    
    def lookForMP(self, disposition):
	"""
	Looks for membrane proteins (MP) in the dataset. If a disposition value is specified looks for MP that meet this constraint.

	arguments:
		disposition: a possible disposition value ('Transmembrane' or 'TM Monotopic')
	
	return:
		a list of protein identifiers in the form of tuples (structure, chain).
	"""
        from ProDaMa.MembraneProtein import MembraneProtein
        return MembraneProtein(self.getIds()).lookForMP(disposition)

    def lookForTMTopology(self, topology):
	"""
	Looks for transmembrane proteins (TM) in the dataset that meet a given constraint on their topology.

	arguments:
		topology: a possible TM topology ('alpha helical' or 'beta barrel')
	
	return:
		a list of protein identifiers in the form of tuples (structure, chain).
	"""
        from ProDaMa.MembraneProtein import MembraneProtein
        return MembraneProtein(self.getIds()).lookForTMTopology(topology)

    def lookForTMSegments(self, **range):
	"""
	Looks for transmembrane proteins (TM) in the datset with a number of TM segments smaller than a minimum value or bigger than a maximum value.  If minimum and maximum values are provided it looks for TM proteins with a number of TM segments between an lower and an upper limit.  

	arguments:
		**range: keys 'MIN' and 'MAX'
	
	return:
		a list of protein identifiers in the form of tuples (structure, chain).
	"""
        from ProDaMa.MembraneProtein import MembraneProtein
        return MembraneProtein(self.getIds()).lookForTMSegments(**range)
    
    def sequencesCull(self,**parameters):
	"""
	Culls (using PISCES) sets of protein sequences from the dataset according to sequence identity and structural criteria. 
    
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
        from ProDaMa.IdentitySearchEngine import IdentitySearchEngine
        return IdentitySearchEngine(self.getIds()).sequencesCullFromPDB(**parameters)

    

    
