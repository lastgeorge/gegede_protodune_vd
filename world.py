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

    def __init__(self, name):
        super(WorldBuilder, self).__init__(name)
        
        # Initialize parameters as None
        self.cryo = None 
        self.tpc = None

        # Add the subbuilders
        for name, builder in self.builders.items():
            self.add_builder(name, builder)
    
    
    def configure(self, material='Air', width=None, height=None, depth=None, 
                 tpc_parameters=None, cryostat_parameters=None, **kwds):
        self.material = material
        self.width = width
        self.height = height 
        self.depth = depth
        
        # Process TPC parameters
        if tpc_parameters:
            # Create a dictionary from the string with proper Quantity objects
            eval_globals = {'Q': Q}
            self.tpc = eval(tpc_parameters, eval_globals)
            
            # Calculate derived TPC parameters
            self.tpc['widthCRP'] = self.tpc['widthPCBActive'] + 2 * self.tpc['borderCRP']
            self.tpc['lengthCRP'] = (2 * self.tpc['lengthPCBActive'] + 
                                   2 * self.tpc['borderCRP'] + 
                                   self.tpc['gapCRU'])

            # Active TPC dimensions based on CRP
            self.tpc['widthTPCActive'] = (self.tpc['nCRM_x']/2) * self.tpc['widthCRP'] 
            self.tpc['lengthTPCActive'] = (self.tpc['nCRM_z']/2) * self.tpc['lengthCRP']

            # Total readout plane thickness
            self.tpc['ReadoutPlane'] = self.tpc['nViews'] * self.tpc['padWidth']

        # Process Cryostat parameters
        if cryostat_parameters:
            eval_globals = {'Q': Q}
            self.cryo = eval(cryostat_parameters, eval_globals)
            
            # Calculate derived parameters
            self.cryo['xLArBuffer'] = (self.cryo['Argon_x'] - 
                                      self.tpc['driftTPCActive'] - 
                                      self.cryo['HeightGaseousAr'] - 
                                      self.tpc['ReadoutPlane'])
            
            self.cryo['Upper_xLArBuffer'] = (self.cryo['Upper_xLArBuffer_base'] - 
                                            self.tpc['ReadoutPlane'])
            
            self.cryo['Lower_xLArBuffer'] = (self.cryo['Lower_xLArBuffer_base'] - 
                                            self.tpc['ReadoutPlane'])
            
            self.cryo['yLArBuffer'] = (self.cryo['Argon_y'] - 
                                      self.tpc['widthTPCActive']) * 0.5
            
            self.cryo['zLArBuffer'] = (self.cryo['Argon_z'] - 
                                      self.tpc['lengthTPCActive']) * 0.5
            
            self.cryo['Cryostat_x'] = self.cryo['Argon_x'] + 2 * self.cryo['SteelThickness']
            self.cryo['Cryostat_y'] = self.cryo['Argon_y'] + 2 * self.cryo['SteelThickness']
            self.cryo['Cryostat_z'] = self.cryo['Argon_z'] + 2 * self.cryo['SteelThickness']


        # Pass parameters to sub builders
        for name, builder in self.builders.items():
            if name == 'detenclosure':
                builder.configure(cryostat_parameters=self.cryo,
                                  tpc_parameters=self.tpc,
                                **kwds)

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
