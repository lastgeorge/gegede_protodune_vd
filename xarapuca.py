#!/usr/bin/env python
'''
xarapuca builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class XARAPUCABuilder(gegede.builder.Builder):
    '''
    Build the Xarapucas for ProtoDUNE-VD.
    Implements both thick and slim field shapers arranged vertically.
    '''