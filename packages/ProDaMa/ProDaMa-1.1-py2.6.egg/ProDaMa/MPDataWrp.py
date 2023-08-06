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
A wrapper for the MPTopo database.
"""


from ProDaMa.services.PDBClient import *
from ProDaMa.model.dbSession import *
from math import sqrt
import httplib

class MPDataWrp(object):
    """
    Retrieves information about membrane proteins (MP) from the MPTopo database.
    """
    
    
    def __isRelevant(self, line):
        """
        Checks if the given string contains information relevant with the classification.
            
        return:
            a boolean value. Returns True if the line contains relevants information, else returns False
        """
        return line and not line.isspace() and ':' in line
    
    def __httpResponseFilter(self,  sequence, response):
        """
        Reads the HTTP response and filters it keeping the data related to the classification.
        """
        where_sequence=response.find('sequence:'+sequence)  
        if where_sequence==-1: return None
        start=response[:where_sequence].rfind('&gt;')
        end=response[where_sequence:].find('&gt;')!=-1 and response[where_sequence:].find('&gt;')+where_sequence or -1
        return response[start:end]
       
    def __getMPTopoClassification(self, sequence):
        """
        Returns a dict containing MPtopo data for given sequence
        """
        httpConnection=httplib.HTTPConnection('blanco.biomol.uci.edu')
        url='/mptopo/mptopodownload.html'
        httpConnection.request('GET',url)
        response=httpConnection.getresponse()
        if response.status==200: response=response.read()
        else: raise httplib.HTTPException()
        response =self.__httpResponseFilter(sequence,response[response.find('&gt;'):response.find('</code>')])
        MP_data = {}
        if response:
            data = [line for line in response.splitlines() if self.__isRelevant(line)]
            for line in data:
                dcom=line.find(':')
                MP_data[line[:dcom].strip()]=line[dcom+1:].strip()
            
            MP_data['first']=response.splitlines()[0].replace('&gt;','')
            return MP_data['sequence'].replace('*','') == sequence and MP_data or None
        else:
            return None

        
    def getData(self, sequence):
        """
        Retrieves information from the MPTopo database for a given sequence, if any.

        arguments:
            sequence: an amino acids sequence

        return:
            if the protein is a membrane protein returns a MPData object, else returns None
        """  
        MPTopo_data=self.__getMPTopoClassification(sequence)
    
        if not MPTopo_data or (MPTopo_data['first'].find('1D')!=-1):
            return None
        data=MPData()
        type_select=(MPTopo_data['protein_name'].find('*')==-1) and MPTopo_data['first'].split(';')[0] or MPTopo_data['first'].split(';')[0]+'*'
        data.topology,data.disposition={'3D_helix':('alpha helical','Transmembrane'), '3D_helix*':('alpha helical','Transmembrane'),'3D_other':('-','TM Monotopic'),'3D_other*':('beta barrel','Transmembrane')}[type_select]
        data.segments=MPTopo_data['tm_segments']
        data.nb_segments=len(data.segments.split(';'))

        segment_sizes = [int(segment.split('.')[1].split(',')[1])-int(segment.split('.')[1].split(',')[0]) for segment in data.segments.split(';')]
        data.segm_avg_length = sum(segment_sizes)/float(len(segment_sizes))
        data.segm_std_deviation = sqrt(sum([pow(x-data.segm_avg_length,2) for x in segment_sizes])/float(len(segment_sizes)))
        return data

    def getDataById(self, protein_id):
        """
        Retrieves information from the MPTopo database for a given protein identifier, if any.
    
        parameters:
            protein_id: a protein identifier in the form (structure, chain)

        return:
            if the protein is a membrane protein returns a MPData object, else returns None
        """
        try:
            return self.getData(Session.query(Chain).filter_by(str_id=protein_id[0],chain_id=protein_id[1]).first().sequence)
        except:
            return None
