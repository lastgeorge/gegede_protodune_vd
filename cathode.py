#!/usr/bin/env python
'''
Cathode builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class CathodeBuilder(gegede.builder.Builder):
    '''Build the cathode structure including mesh'''

    # Define default parameters that can be overridden in configuration
    defaults = dict(
        # Basic cathode frame parameters
        heightCathode = Q("6.0cm"),
        CathodeBorder = Q("4.0cm"),
        widthCathodeVoid = Q("77.25cm"),  
        lengthCathodeVoid = Q("67.25cm"),

        # Cathode mesh parameters  
        CathodeMeshInnerStructureWidth = Q("0.25cm"),
        CathodeMeshInnerStructureThickness = Q("0.05cm"),
        CathodeMeshInnerStructureSeparation = Q("2.5cm"),
        CathodeMeshInnerStructureNumberOfStrips_vertical = 30,
        CathodeMeshInnerStructureNumberOfStrips_horizontal = 26,
        
        # Cathode frame offset
        CathodeMeshOffset_Y = Q("87.625cm")
    )

    def configure(self, tpc_params=None, **kwargs):
        """Configure the cathode geometry.
        
        Args:
            tpc_params (dict): TPC parameters from parent builder
            **kwargs: Additional configuration parameters
        """
        # Start with defaults
        self.params = self.defaults.copy()
        
        # Update with any overrides from kwargs
        self.params.update(kwargs)
        
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