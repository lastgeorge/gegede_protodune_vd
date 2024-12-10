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

    def configure(self, 
                 FieldShaperInnerRadius=None,
                 FieldShaperOuterRadius=None,
                 FieldShaperSlimInnerRadius=None, 
                 FieldShaperSlimOuterRadius=None,
                 FieldShaperTorRad=None,
                 FieldShaperSeparation=None,
                 NFieldShapers=None,
                 FieldShaperBaseLength=None,
                 FieldShaperBaseWidth=None,
                 **kwds):
        
        # Add guard against double configuration
        if hasattr(self, '_configured'):
            return
            
        # Store basic parameters
        self.params = {}
        self.params.update(
            FieldShaperInnerRadius = FieldShaperInnerRadius,
            FieldShaperOuterRadius = FieldShaperOuterRadius,
            FieldShaperSlimInnerRadius = FieldShaperSlimInnerRadius,
            FieldShaperSlimOuterRadius = FieldShaperSlimOuterRadius,
            FieldShaperTorRad = FieldShaperTorRad,
            FieldShaperSeparation = FieldShaperSeparation,
            NFieldShapers = NFieldShapers
        )

        # Calculate derived dimensions
        # Length and width account for torus radius at ends
        self.params['FieldShaperLength'] = FieldShaperBaseLength - 2*FieldShaperTorRad
        self.params['FieldShaperWidth'] = FieldShaperBaseWidth - 2*FieldShaperTorRad
        
        # Add small extension for cuts
        self.params['FieldShaperCutLength'] = self.params['FieldShaperLength'] + Q('0.02cm')
        self.params['FieldShaperCutWidth'] = self.params['FieldShaperWidth'] + Q('0.02cm')

        # Calculate overall field cage dimensions
        self.params['FieldCageSizeX'] = FieldShaperSeparation * NFieldShapers + Q('2cm')
        self.params['FieldCageSizeY'] = self.params['FieldShaperWidth'] + Q('2cm') 
        self.params['FieldCageSizeZ'] = self.params['FieldShaperLength'] + Q('2cm')

        # Mark as configured
        self._configured = True