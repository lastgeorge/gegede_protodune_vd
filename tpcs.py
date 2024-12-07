#!/usr/bin/env python
'''
TPC (Time Projection Chamber) builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class TPCBuilder(gegede.builder.Builder):
    '''
    Build the TPC volumes including wire planes
    '''