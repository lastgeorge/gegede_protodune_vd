#!/usr/bin/env python
'''
Main builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

# Import the CryostatBuilder
from cryostat import CryostatBuilder
from foam import FoamBuilder
from steelsupport import SteelSupportBuilder
from beamelements import BeamElementsBuilder

class ProtoDUNEVDBuilder(gegede.builder.Builder):
    '''
    Build the ProtoDUNE-VD detector enclosure and components
    '''

    def __init__(self, name):
        super(ProtoDUNEVDBuilder, self).__init__(name)
        
        # Initialize parameters as None
        self.cryo = None 
        self.tpc = None

        # Add the subbuilders
        for name, builder in self.builders.items():
            self.add_builder(name, builder)

    def configure(self, cryostat_parameters=None, tpc_parameters=None, **kwds):
        
        # Store the parameters
        if cryostat_parameters:
            self.cryo = cryostat_parameters
        if tpc_parameters:
            self.tpc = tpc_parameters

        # Pass parameters to sub builders
        for name, builder in self.builders.items():
            if name == 'cryostat':
                builder.configure(cryostat_parameters=self.cryo,
                                  tpc_parameters=self.tpc, 
                                **kwds)

    def construct(self, geom):
        '''
        Construct the geometry.
        '''
        

        # Create the main volume
        main_shape = geom.shapes.Box(self.name + '_shape',
                                   dx=Q('1500cm'),
                                   dy=Q('1500cm'),
                                   dz=Q('1500cm'))
        
        main_lv = geom.structure.Volume(self.name, 
                                      material='Air',
                                      shape=main_shape)

        # Construct and place all subbuilders
        # for builder in self.get_builders():
        #     if builder.volumes is not None:
        #         vol = builder.get_volume()
        #         name = vol.name + '_place'
        #         pos = geom.structure.Placement(name, volume=vol)
        #         main_lv.placements.append(pos.name)

        self.add_volume(main_lv)
