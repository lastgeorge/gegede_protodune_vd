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
                 **kwargs):
        
        print('Configure Foam')
        
        self.params = {
            'FoamPadding': FoamPadding
        }

