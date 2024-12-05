#!/usr/bin/env python
'''
World builder for ProtoDUNE-VD
'''

import gegede.builder
from gegede import Quantity as Q

class WorldBuilder(gegede.builder.Builder):
    '''
    Build the world volume which will contain the full detector
    '''
    
    def configure(self, material='Air', width=None, height=None, depth=None, **kwds):
        self.material = material
        self.width = width
        self.height = height 
        self.depth = depth

    def construct(self, geom):
        shape = geom.shapes.Box(self.name + '_shape', 
                              dx=self.width/2.0,
                              dy=self.height/2.0,
                              dz=self.depth/2.0)
        
        volume = geom.structure.Volume(self.name + '_volume',
                                     material=self.material,
                                     shape=shape)
        
        self.add_volume(volume)

        # Place daughter volumes
        for name, builder in self.builders.items():
            if builder.volumes:
                daughter = builder.get_volume()
                pname = f'{daughter.name}_in_{self.name}'
                place = geom.structure.Placement(pname, volume=daughter)
                volume.placements.append(pname)
