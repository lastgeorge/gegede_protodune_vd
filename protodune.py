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

    def configure(self, 
                 tpc_parameters= "{'inch': 2.54, 'nChans': {'Ind1': 476, 'Ind2': 476, 'Col': 584}, 'nViews': 3, 'wirePitch': {'U': Q('0.765cm'), 'V': Q('0.765cm'), 'Z': Q('0.51cm')}, 'wireAngle': {'U': Q('150.0deg'), 'V': Q('30.0deg')}, 'offsetUVwire': [Q('1.50cm'), Q('0.87cm')], 'lengthPCBActive': Q('149.0cm'), 'widthPCBActive': Q('335.8cm'), 'gapCRU': Q('0.1cm'), 'borderCRP': Q('0.6cm'), 'nCRM_x': 4, 'nCRM_z': 2, 'padWidth': Q('0.02cm'), 'driftTPCActive': Q('338.5cm')}",
                 cryostat_parameters = "{'Argon_x': Q('789.6cm'), 'Argon_y': Q('854.4cm'), 'Argon_z': Q('854.4cm'), 'HeightGaseousAr': Q('49.7cm'), 'SteelThickness': Q('0.2cm'), 'Upper_xLArBuffer_base': Q('23.6cm'), 'Lower_xLArBuffer_base': Q('34.7cm')}",
                 **kwds):
        
        # Process TPC parameters
        if tpc_parameters:
            # Create a dictionary from the string with proper Quantity objects
            # First create a dict where Q() is defined
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

        # Pass parameters to sub builders ... 
        for name, builder in self.builders.items():
            if name == 'cryostat':
                builder.configure(tpc_parameters=self.tpc, 
                                cryostat_parameters=self.cryo,
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
