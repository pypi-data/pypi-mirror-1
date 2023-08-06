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
A protein CATH classification.
"""

class CATHProteinData(object):
    """
    This class must be used to represents the CATH classification of a protein.
    """
    
    def __init__(self, data=None):
        """
        Defines the CATH data.
        
        arguments:
            data: the CATH data for a classified protein. It is a dictionary with keys the CATH hierarchical levels.
        """
        if data:
            self.cath_code=data['CATH code']
            self.Class=data['Class']
            self.architecture=data['Architecture']
            self.topology=data['Topology']
            self.homologous=data['Homologous superfamily']
        
