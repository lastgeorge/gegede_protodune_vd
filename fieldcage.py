#!/usr/bin/env python
'''
Field Cage builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class FieldCageBuilder(gegede.builder.Builder):
    '''
    Build the field cage for ProtoDUNE-VD.
    Implements both thick and slim field shapers arranged vertically.
    '''