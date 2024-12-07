#!/usr/bin/env python
'''
PMTs builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class PMTBuilder(gegede.builder.Builder):
    '''
    Build the PMTs for ProtoDUNE-VD.
    Implements both thick and slim field shapers arranged vertically.
    '''