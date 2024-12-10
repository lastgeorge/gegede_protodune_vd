#!/usr/bin/env python
'''
Cryostat builder for ProtoDUNE-VD geometry 
'''

import gegede.builder
from gegede import Quantity as Q

from fieldcage import FieldCageBuilder
from cathode import CathodeBuilder
from tpcs import TPCBuilder
from pmts import PMTBuilder
from xarapuca import XARAPUCABuilder

class CryostatBuilder(gegede.builder.Builder):
    '''
    Build the ProtoDUNE-VD cryostat
    '''
    
    def __init__(self, name):
        super(CryostatBuilder, self).__init__(name)
        
        # Initialize parameters as None
        self.cryo = None 
        self.tpc = None
        self.cathode = None

        # # Add the subbuilders
        # for name, builder in self.builders.items():
        #     self.add_builder(name, builder)

    def configure(self, cryostat_parameters=None, tpc_parameters=None, 
                 cathode_parameters=None, xarapuca_parameters=None, **kwds):  # Add xarapuca_parameters

        # Add guard against double configuration
        if hasattr(self, '_configured'):
            return
        
        # Store the parameters
        if cryostat_parameters:
            self.cryo = cryostat_parameters
        if tpc_parameters:
            self.tpc = tpc_parameters
        if cathode_parameters:
            self.cathode = cathode_parameters
        if xarapuca_parameters:  # Add this block
            self.xarapuca = xarapuca_parameters
        
        # Mark as configured
        self._configured = True

        #Pass parameters to subbuilders
        for name, builder in self.builders.items():
            if name == 'tpcs':
                builder.configure(tpc_parameters=self.tpc,
                                **kwds)
            elif name == 'cathode':
                builder.configure(tpc_params=self.tpc,
                                cathode_parameters=self.cathode,  # Add this line
                                **kwds)
            elif name == 'xarapuca':
                builder.configure(xarapuca_parameters=self.xarapuca,
                                **kwds)



    def construct(self, geom):
        '''Construct the cryostat and place components'''
        
        # Create the main cryostat shape
        cryo_shape = geom.shapes.Box(self.name + '_shape',
                                dx=self.cryo['Cryostat_x']/2.0,
                                dy=self.cryo['Cryostat_y']/2.0, 
                                dz=self.cryo['Cryostat_z']/2.0)

        # Create the argon volume shape
        argon_shape = geom.shapes.Box(self.name + '_argon_shape',
                                    dx=self.cryo['Argon_x']/2.0,
                                    dy=self.cryo['Argon_y']/2.0,
                                    dz=self.cryo['Argon_z']/2.0)

        # Create gaseous argon volume
        gas_ar_shape = geom.shapes.Box(self.name + '_gasAr_shape',
                                    dx=self.cryo['HeightGaseousAr']/2.0,
                                    dy=self.cryo['Argon_y']/2.0,
                                    dz=self.cryo['Argon_z']/2.0)

        # # Subtract X-ARAPUCA spaces from gaseous argon
        # arapuca_pos1 = [-0.5*self.cryo['HeightGaseousAr'] - self.cryo['Upper_xLArBuffer'] - 
        #                 self.tpc['FirstFrameVertDist'] - self.tpc['ReadoutPlane'],
        #                 -self.tpc['widthCathode'] - self.tpc['CathodeFrameToFC'] - 
        #                 self.tpc['FCToArapucaSpaceLat'],
        #                 -0.5*self.cryo['Argon_z'] + self.cryo['zLArBuffer'] + 
        #                 0.5*self.tpc['lengthCathode']]
                        
        # gas_ar_sub1 = geom.shapes.Boolean(self.name + '_gasAr_sub1',
        #                                 type='subtraction',
        #                                 first=gas_ar_shape,
        #                                 second=self.get_builder('xarapuca').get_volume().shape,
        #                                 pos=arapuca_pos1)

        # # Second X-ARAPUCA subtraction with updated Y position
        # arapuca_pos2 = [arapuca_pos1[0],
        #                 -arapuca_pos1[1],  # Flip Y position
        #                 arapuca_pos1[2]]
                        
        # gas_ar_shape_final = geom.shapes.Boolean(self.name + '_gasAr_final',
        #                                     type='subtraction',
        #                                     first=gas_ar_sub1,
        #                                     second=self.get_builder('xarapuca').get_volume().shape,
        #                                     pos=arapuca_pos2)

        # Create the steel shell by subtracting argon volume from cryostat
        steel_shape = geom.shapes.Boolean(self.name + '_steel_shape',
                                        type='subtraction',
                                        first=cryo_shape,
                                        second=argon_shape)

        # Create volumes
        steel_vol = geom.structure.Volume(self.name + '_steel_volume',
                                        material='STEEL_STAINLESS_Fe7Cr2Ni',
                                        shape=steel_shape)
        
        argon_vol = geom.structure.Volume(self.name + '_argon_volume',
                                        material='LAr', 
                                        shape=argon_shape)

        gas_ar_vol = geom.structure.Volume(self.name + '_gasAr_volume',
                                        material='GAr',
                                        # shape=gas_ar_shape_final)
                                        shape=gas_ar_shape)

        # Create the main cryostat volume
        cryo_vol = geom.structure.Volume(self.name + '_volume',
                                    material='Air',
                                    shape=cryo_shape)

        # Create and place gaseous argon volume
        gas_ar_pos = geom.structure.Position("gas_ar_pos",
                                        x=self.cryo['Argon_x']/2.0 - self.cryo['HeightGaseousAr']/2.0,
                                        y=Q('0cm'),
                                        z=Q('0cm'))
        
        gas_ar_place = geom.structure.Placement(self.name + '_gasAr_place',
                                            volume=gas_ar_vol,
                                            pos=gas_ar_pos)
        
        # Create positions for steel and argon volumes
        steel_pos = geom.structure.Position("steel_pos", x=Q('0cm'), y=Q('0cm'), z=Q('0cm'))
        argon_pos = geom.structure.Position("argon_pos", x=Q('0cm'), y=Q('0cm'), z=Q('0cm'))
        
        # Create placements using the position objects
        steel_place = geom.structure.Placement(self.name + '_steel_place',
                                        volume=steel_vol,
                                        pos=steel_pos)
        argon_place = geom.structure.Placement(self.name + '_argon_place',
                                        volume=argon_vol, 
                                        pos=argon_pos)
        
        cryo_vol.placements.append(steel_place.name)
        cryo_vol.placements.append(argon_place.name)
        argon_vol.placements.append(gas_ar_place.name)


        self.add_volume(cryo_vol)