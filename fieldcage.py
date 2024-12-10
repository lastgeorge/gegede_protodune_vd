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
                 fieldcage_parameters=None,
                 **kwds):
        
        print('Configure Field Cage')
        # Add guard against double configuration
        if hasattr(self, '_configured'):
            return
        
        if fieldcage_parameters:
            self.inner_radius = fieldcage_parameters.get('FieldShaperInnerRadius')
            self.outer_radius = fieldcage_parameters.get('FieldShaperOuterRadius')
            self.slim_inner_radius = fieldcage_parameters.get('FieldShaperSlimInnerRadius')
            self.slim_outer_radius = fieldcage_parameters.get('FieldShaperSlimOuterRadius')
            self.tor_rad = fieldcage_parameters.get('FieldShaperTorRad')
            self.separation = fieldcage_parameters.get('FieldShaperSeparation') 
            self.n_shapers = fieldcage_parameters.get('NFieldShapers')
            self.base_length = fieldcage_parameters.get('FieldShaperBaseLength')
            self.base_width = fieldcage_parameters.get('FieldShaperBaseWidth')

            # Calculate derived dimensions
            self.length = self.base_length - 2*self.tor_rad
            self.width = self.base_width - 2*self.tor_rad
            
            self.cut_length = self.length + Q('0.02cm')
            self.cut_width = self.width + Q('0.02cm')

            self.cage_size_x = self.separation * self.n_shapers + Q('2cm')
            self.cage_size_y = self.width + Q('2cm') 
            self.cage_size_z = self.length + Q('2cm')

        # Mark as configured
        self._configured = True