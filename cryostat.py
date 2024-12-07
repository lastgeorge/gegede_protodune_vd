#!/usr/bin/env python
'''
Cryostat builder for ProtoDUNE-VD geometry 
'''

import gegede.builder
from gegede import Quantity as Q

from fieldcage import FieldCageBuilder
from cathode import CathodeBuilder
from tpcs import TPCBuilder
from pmts import PMTBuilder
from xarapuca import XARAPUCABuilder

class CryostatBuilder(gegede.builder.Builder):
    '''
    Build the ProtoDUNE-VD cryostat
    '''