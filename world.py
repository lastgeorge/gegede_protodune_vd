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
        self.steel = None

        # Add the subbuilders
        for name, builder in self.builders.items():
            self.add_builder(name, builder)
    

    def configure(self, material='Air', width=None, height=None, depth=None, 
                 tpc_parameters=None, cryostat_parameters=None, 
                 steel_parameters=None, FoamPadding=None, AirThickness=None,
                 DP_CRT_switch=None, **kwds):
        self.material = material
        self.width = width
        self.height = height 
        self.depth = depth
        
        # Add the parameters that were moved out
        self.FoamPadding = FoamPadding
        self.AirThickness = AirThickness
        self.DP_CRT_switch = DP_CRT_switch

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


         # Process Steel Support parameters
        if steel_parameters:
            eval_globals = {'Q': Q}
            self.steel = eval(steel_parameters, eval_globals)

            # Calculate detector enclosure dimensions
            self.steel['DetEncX'] = (self.cryo['Cryostat_x'] + 
                                    2*(self.steel['SteelSupport_x'] + self.FoamPadding) + 
                                    2*self.steel['SpaceSteelSupportToWall'])
            
            self.steel['DetEncY'] = (self.cryo['Cryostat_y'] + 
                                    2*(self.steel['SteelSupport_y'] + self.FoamPadding) + 
                                    self.steel['SpaceSteelSupportToCeiling'])
            
            self.steel['DetEncZ'] = (self.cryo['Cryostat_z'] + 
                                    2*(self.steel['SteelSupport_z'] + self.FoamPadding) + 
                                    2*self.steel['SpaceSteelSupportToWall'])

            # Calculate position parameters
            self.steel['posCryoInDetEnc'] = {'x': Q('0cm'), 
                                            'y': Q('0cm'), 
                                            'z': Q('0cm')}

            # Calculate steel structure positions
            self.steel['posTopSteelStruct'] = (self.cryo['Argon_y']/2 + 
                                            self.FoamPadding + 
                                            self.steel['SteelSupport_y'])
            
            self.steel['posBotSteelStruct'] = -(self.cryo['Argon_y']/2 + 
                                            self.FoamPadding + 
                                            self.steel['SteelSupport_y'])
            
            self.steel['posZBackSteelStruct'] = (self.cryo['Argon_z']/2 + 
                                                self.FoamPadding + 
                                                self.steel['SteelSupport_z'])
            
            self.steel['posZFrontSteelStruct'] = -(self.cryo['Argon_z']/2 + 
                                                self.FoamPadding + 
                                                self.steel['SteelSupport_z'])
            
            self.steel['posLeftSteelStruct'] = (self.cryo['Argon_x']/2 + 
                                            self.FoamPadding + 
                                            self.steel['SteelSupport_x'])
            
            self.steel['posRightSteelStruct'] = -(self.cryo['Argon_x']/2 + 
                                                self.FoamPadding + 
                                                self.steel['SteelSupport_x'])

            # Adjust for CRT if needed  
            if self.DP_CRT_switch == True:
                self.steel['posTopSteelStruct'] -= Q('29.7cm')
                self.steel['posBotSteelStruct'] += Q('29.7cm')

            # Calculate origin positions
            self.steel['OriginZSet'] = (self.steel['DetEncZ']/2.0 -
                                    self.steel['SpaceSteelSupportToWall'] -
                                    self.steel['SteelSupport_z'] -
                                    self.FoamPadding -
                                    self.cryo['SteelThickness'] -
                                    self.cryo['zLArBuffer'])

            self.steel['OriginYSet'] = (self.steel['DetEncY']/2.0 -
                                    self.steel['SpaceSteelSupportToCeiling']/2.0 -
                                    self.steel['SteelSupport_y'] -
                                    self.FoamPadding -
                                    self.cryo['SteelThickness'] -
                                    self.cryo['yLArBuffer'] -
                                    self.tpc['widthTPCActive']/2)

            self.steel['OriginXSet'] = (self.steel['DetEncX']/2.0 -
                                    self.steel['SpaceSteelSupportToWall'] -
                                    self.steel['SteelSupport_x'] -
                                    self.FoamPadding -
                                    self.cryo['SteelThickness'] -
                                    self.cryo['xLArBuffer'] +
                                    Q('6.0cm')/2 +  # heightCathode/2
                                    self.cryo['Upper_xLArBuffer'])

        # Pass parameters to sub builders
        for name, builder in self.builders.items():
            if name == 'detenclosure':
                builder.configure(cryostat_parameters=self.cryo,
                                  tpc_parameters=self.tpc,
                                  steel_parameters=self.steel,
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
