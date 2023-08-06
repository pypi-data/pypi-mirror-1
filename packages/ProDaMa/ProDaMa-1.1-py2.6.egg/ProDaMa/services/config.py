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
This module defines variables useful for the installation of the library. The file is written during the installation process. The user can use this file to change the installation settings.
"""

DB_ENGINE = "" # the db engine

DB_NAME = "" # database name

DB_USER = "" # database user account: user name

DB_PASSWORD = "" # database user account: user password

DB_HOST = "" # the url of the database

DB_PORT = "" # the MySQL port

EMAIL = "" # used to invoke PSI-BLAST

DATA ="" # here the path of a writable directory to be used for temporany data

PISCES ="" # here the path of  the PISCES installation

PSIBLAST ="" # here the path of PSI-BLAST perl client
