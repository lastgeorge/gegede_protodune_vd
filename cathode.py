#!/usr/bin/env python
'''
Cathode builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class CathodeBuilder(gegede.builder.Builder):
    '''Build the cathode structure including mesh'''

    def __init__(self, name):
        super(CathodeBuilder, self).__init__(name)
        self.params = None

    def configure(self, cathode_parameters=None, tpc_params=None, **kwargs):
        """Configure the cathode geometry.
        
        Args:
            cathode_parameters (dict): Cathode parameters from config
            tpc_params (dict): TPC parameters from parent builder
            **kwargs: Additional configuration parameters
        """
        print('Configure Cathode')
        # Add guard against double configuration
        if hasattr(self, '_configured'):
            return
            
        # Store cathode params
        if cathode_parameters:
            self.params = cathode_parameters
        
        # Store TPC params we need
        if tpc_params:
            # Set width and length based on CRP dimensions
            self.params['widthCathode'] = tpc_params['widthCRP']
            self.params['lengthCathode'] = tpc_params['lengthCRP']
            
            # Set mesh dimensions based on void dimensions
            self.params['CathodeMeshInnerStructureLength_vertical'] = \
                self.params['lengthCathodeVoid']
            self.params['CathodeMeshInnerStructureLength_horizontal'] = \
                self.params['widthCathodeVoid']

        # Update with any overrides from kwargs
        if kwargs:
            self.params.update(kwargs)
            
        # Mark as configured
        self._configured = True

    def construct(self, geom):
        '''Construct the cathode geometry'''
        # TODO: Add cathode construction code
        pass