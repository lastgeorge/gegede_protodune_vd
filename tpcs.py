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
    def __init__(self, name):
        super(TPCBuilder, self).__init__(name)
        
        # Initialize parameters as None
        self.tpc = None

        # Add the subbuilders
        for name, builder in self.builders.items():
            self.add_builder(name, builder)

    def configure(self, tpc_parameters=None, **kwds):
        # Store the parameters
        if tpc_parameters:
            self.tpc = tpc_parameters
        

