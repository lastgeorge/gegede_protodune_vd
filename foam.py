#!/usr/bin/env python
'''
Foam Builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class FoamBuilder(gegede.builder.Builder):
    '''Build the foam for ProtoDUNE-VD'''

    def configure(self,
                 FoamPadding=None,
                 print_config=False,  
                 print_construct=False,  # Add this line
                 **kwargs):
        
        if print_config:
            print('Configure Foam <- ProtoDUNE-VD <- World')
        
        self.print_construct = print_construct

        self.params = {
            'FoamPadding': FoamPadding
        }

    def construct(self, geom):
        if self.print_construct:
            print('Construct Foam <- ProtoDUNE-VD <- World')
        # TODO: Add Foam construction code

