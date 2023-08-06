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
An interface to PISCES.
"""

from subprocess import Popen, PIPE
from config import PISCES, DATA
import os

def cullFromPDB(target_dset, MAX_percentage_identity=25, MIN_resolution=0.0, MAX_resolution=2.5, MIN_chain_length=20, MAX_chain_length=400, RFactor=0.3, skip_non_x=True, skip_CA_only=True):
    """
    Invokes PISCES.
    
    arguments:
        target_dset: the target dataset
        MAX_percentage_identity=25: the constraint for the sequence identity
        MIN_resolution=0.0: a lower limit for the resolution
        MAX_resolution=2.5: an upper limit for the resolution
        MIN_chain_length=20: a lower limit for the chain length
        MAX_chain_length=400: an upper limit for the chain length
        RFactor=0.3: the R factor
        skip_non_x=True,
        skip_CA_only=True
    
    return:
        a list of protein identifiers
    """
   
    service_file_name = "pidslist.txt"
    __createInputFile(target_dset, service_file_name)
    
    arguments = " -i %s -p %s -r %s-%s -l %s-%s -f %s -x %s -a %s" \
                %("%s/%s"%(DATA,service_file_name),str(MAX_percentage_identity),str(MIN_resolution),str(MAX_resolution),
                  str(MIN_chain_length),str(MAX_chain_length),str(RFactor),skip_non_x and 'T' or 'F', skip_CA_only and 'T' or 'F')
    cwd=os.getcwd()
    os.chdir(DATA)
    process=Popen("%s/bin/Cull_for_UserPDB.pl"%PISCES+arguments,stdout=PIPE, shell=True)
    process.wait()
    os.chdir(cwd)
    return __getPISCESResponse()
    

def __createInputFile(target_dset, filename):
    """
    Generates a service file that contains the target dataset. The file is used by PISCES
    
    arguments:
        target_dset: the target dataset
        
        filename: the name of the service file
    
    return:
        the name of the service file
    """
    
    if not target_dset: target_dset=['whole']
    file_name="%s/%s"%(DATA,filename)
    list_file=open(file_name,'w')
    for pid in target_dset:
        list_file.write("%s\n"%pid.replace(':',''))
    list_file.close()
    


def __getPISCESResponse():
    """
    Reads the result of PISCES to gets the protein identifiers.
    
    return:
        a list of protein identifiers in the form of tuples (structure, chain)
    """
    listdir = os.listdir(DATA)
    filename = [filename for filename in listdir if filename.find('cullpdb')!=-1 and filename.find('fasta')==-1][0]
    outputPISCES = open(DATA+'/'+filename,'r')
    protein_ids = [line.split(' ')[0] for line in outputPISCES.readlines()]
    outputPISCES.close()
    for file_to_remove in [DATA+'/'+filename for filename in listdir if filename.find('cull')!=-1 or filename.find('log')!=-1]:
        os.remove(file_to_remove)
    return protein_ids[1:]
 



