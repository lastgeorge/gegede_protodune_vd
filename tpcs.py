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

    def configure(self, tpc_parameters=None, print_config=False, print_construct=False, **kwds):
        if print_config:
            print('Configure TPC <- Cryostat <- ProtoDUNE-VD <- World')
        if (hasattr(self, '_configured')):
            return 
        # Store the parameters
        if tpc_parameters:
            self.tpc = tpc_parameters

        self.print_construct = print_construct
        self._configured = True

    def construct(self, geom):
        if self.print_construct:
            print('Construct TPC <- Cryostat <- ProtoDUNE-VD <- World')
        # ...existing code...


