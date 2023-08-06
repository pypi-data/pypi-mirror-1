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
A wrapper for the EBI web server, to retrieve information about CATH and SCOP classified proteins.
"""

from ProDaMa.model.dbSession import *
import httplib



class EBIWrp (object):
    """
    Retrieves information about SCOP classified proteins.
    """
    def __remove_tags(self, line):
        """
        Removes html/xml tags from an input string.
        """
        while '<' in line:
            start = line.rfind('<')
            end = line.rfind('>')
            line = line[:start]+line[end+1:]
        return line
        
    def __isRelevant(self,  line):
        """
        Checks if the given string contains information relevant with the CATH or SCOP protein classification.
        
        return:
            a boolean value. Returns True if the line contains information about the classification, else returns False
        """
        return line and not line.isspace() and len([line_part for line_part in line.split(' ') if line_part])>1
        
    def __httpResponseFilter(self,  response):
        """
        Reads the HTTP response and filters it keeping the data related to the protein CATH or SCOP classification.
        """
        start=response.rfind('<table class="content_table">')
        end=response.rfind('<table class="footerpane"')
        response = response[start:end]
        return [line for line in [self.__remove_tags(i) for i in response.replace('\n','').replace('  ','').split('</tr>')] if self.__isRelevant(line)]

    
    def __getClassification(self, url):
        """
        Gets the page related to the given URL (SCOP and CATH EBI retrieval pages) and reads the relevant data.
        """
        httpConnection = httplib.HTTPConnection('www.ebi.ac.uk')
        httpConnection.request('GET',url)
        response = httpConnection.getresponse()
        if response.status==200: response=response.read()
        else: raise httplib.HTTPException()
        response = self.__httpResponseFilter(response)[1:]
        protein_classification = {}
        for data in response:
            levels = [level.strip() for level in data.split('   ') if level]
            protein_classification[levels[0]] = ' '.join(levels[1:])
        return protein_classification

    
    def getSCOPClassification(self, str_id):
        """
        Given a structure identifier retrieves a SCOP classification.

        parameters:
            str_id: a structure protein identifier

        return:
            if the protein is SCOP classified returns a SCOPProteinData object, else returns None
        """
        try:
            return self.__getClassification('/pdbe-srv/view/entry/%s/refscop'%str_id.lower())
        except:
            return None

    def getCATHClassification(self, str_id):
        """
        Given a structure identifier retrieves a CATH classification.

        parameters:
            str_id: a structure protein identifier

        return:
            if the protein is CATH classified returns a CATHProteinData object, else returns None
        """
        try:
            return self.__getClassification('/pdbe-srv/view/entry/%s/refcath'%str_id.lower())
        except:
            return None
            
 
