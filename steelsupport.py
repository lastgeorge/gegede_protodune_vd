#!/usr/bin/env python
'''
Steel Builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class SteelSupportBuilder(gegede.builder.Builder):
    '''Build the steel support structure for ProtoDUNE-VD'''

    def configure(self,
                 steel_parameters=None,
                 print_config=False,  
                 print_construct=False,  # Add this line
                 **kwargs):
        
        if print_config:
            print('Configure Steel Support  <- ProtoDUNE-VD <- World')
        
        self.print_construct = print_construct

        if steel_parameters:
            self.params = {
                'SteelSupport_x': steel_parameters.get('SteelSupport_x'),
                'SteelSupport_y': steel_parameters.get('SteelSupport_y'),
                'SteelSupport_z': steel_parameters.get('SteelSupport_z'),
                'SteelPlate': steel_parameters.get('SteelPlate'),
                'FracMassOfSteel': steel_parameters.get('FracMassOfSteel'),
                'FracMassOfAir': steel_parameters.get('FracMassOfAir'),
                'SpaceSteelSupportToWall': steel_parameters.get('SpaceSteelSupportToWall'),
                'SpaceSteelSupportToCeiling': steel_parameters.get('SpaceSteelSupportToCeiling')
            }
        
    # ...existing code...

    def construct(self, geom):
        if self.print_construct:
            print('Construct Steel Support <- ProtoDUNE-VD <- World') 
        # TODO: Add Steel Support construction code