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
#Temporary interface to the db.

import sqlalchemy as sa
from sqlalchemy import orm
import datetime
import cPickle
import traceback
from ProDaMa.Dataset import Dataset
from ProDaMa.Chain import Chain
from ProDaMa.Protein import Protein
from ProDaMa.model.CATHProteinData import CATHProteinData
from ProDaMa.model.SCOPProteinData import SCOPProteinData
from ProDaMa.services.config import *

# engine and metadata

engine = sa.create_engine("%s://%s:%s@%s:%s/%s"%(DB_ENGINE,DB_USER,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME))
metadata = sa.MetaData(engine)


# tables
protein_table = sa.Table('Protein',metadata, autoload = True, autoload_with = engine)
chain_table = sa.Table('chain',metadata, autoload = True, autoload_with = engine)
membership_table = sa.Table('membership', metadata, autoload = True, autoload_with = engine)
dataset_table = sa.Table('dataset', metadata, autoload = True, autoload_with = engine)
CATH_table = sa.Table('CATHProteinData',metadata,autoload = True, autoload_with = engine)
SCOP_table = sa.Table('SCOPProteinData',metadata,autoload = True, autoload_with = engine)
membraneprotein_table = sa.Table('MembraneProteinData', metadata, autoload = True, autoload_with = engine)
aadata_table = sa.Table('aadata', metadata, autoload=True, autoload_with = engine)



# classes
class Membership(object):
        pass

class MPData(object):
    pass

class AAData(object):
    pass

# mapping
orm.mapper(AAData, aadata_table)
orm.mapper(Dataset, dataset_table)

orm.mapper(Protein, protein_table, properties = {'chains':orm.relation(Chain, primaryjoin = protein_table.c.str_id == chain_table.c.str_id,
                                                                        backref = 'protein')})

orm.mapper(Chain, chain_table, properties =  {'datasets':orm.relation(Dataset, secondary = membership_table,
                                                           primaryjoin = sa.and_(chain_table.c.str_id == membership_table.c.str_id, chain_table.c.chain_id == membership_table.c.chain_id),
                                                           secondaryjoin = dataset_table.c.name == membership_table.c.dataset_name,
                                                           backref = 'chains')})

orm.mapper(CATHProteinData,  CATH_table,  properties = {'protein':orm.relation(Protein, backref = 'cathClassification')})
orm.mapper(SCOPProteinData,  SCOP_table,  properties = {'protein':orm.relation(Protein, backref = 'scopClassification')})
orm.mapper(MPData,  membraneprotein_table,
                properties = {'mp_chain':orm.relation(Chain,
                primaryjoin = sa.and_(chain_table.c.str_id == membraneprotein_table.c.str_id, chain_table.c.chain_id == membraneprotein_table.c.chain_id), backref = 'mpData')})


# session
sm = orm.sessionmaker(bind = engine)
Session = orm.scoped_session(sm)

