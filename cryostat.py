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
        self.xarapuca = None
        self.fieldcage = None
        self.pmt = None

        # # Add the subbuilders
        # for name, builder in self.builders.items():
        #     self.add_builder(name, builder)

    def configure(self, cryostat_parameters=None, tpc_parameters=None, 
                 cathode_parameters=None, xarapuca_parameters=None, 
                 fieldcage_parameters=None, pmt_parameters=None,  
                 cathode_switch=True, fieldcage_switch=True, arapucamesh_switch=True,  # Add these lines
                 print_config=False,  
                 print_construct=False,  
                 **kwds):  

        if print_config:
            print('Configure Cryostat <- ProtoDUNE-VD <- World')
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
        if xarapuca_parameters:  
            self.xarapuca = xarapuca_parameters
        
        self.cathode_switch = cathode_switch  # Add this line
        self.fieldcage_switch = fieldcage_switch  # Add this line
        self.arapucamesh_switch = arapucamesh_switch  # Add this line

        self.print_config = print_config
        self.print_construct = print_construct
        # Mark as configured
        self._configured = True

        #Pass parameters to subbuilders
        for name, builder in self.builders.items():
            if name == 'tpcs':
                builder.configure(tpc_parameters=self.tpc,
                                  print_config=print_config,
                                  print_construct=print_construct,  
                                  **kwds)
            elif name == 'cathode':
                builder.configure(tpc_params=self.tpc,
                                  cathode_parameters=self.cathode,
                                  print_config=print_config,
                                  print_construct=print_construct,  
                                  **kwds)
            elif name == 'xarapuca':
                builder.configure(xarapuca_parameters=self.xarapuca,
                                  cathode_parameters=self.cathode,
                                  print_config=print_config,
                                  print_construct=print_construct,  
                                  **kwds)
            elif name == 'fieldcage':
                builder.configure(fieldcage_parameters=fieldcage_parameters,
                                  print_config=print_config,
                                  print_construct=print_construct,  
                                  **kwds)
            elif name == 'pmts':
                builder.configure(pmt_parameters=pmt_parameters,
                                  print_config=print_config,
                                  print_construct=print_construct,  
                                  **kwds)

    def construct(self, geom):
        if self.print_construct:
            print('Construct Cryostat <- ProtoDUNE-VD <- World')
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
        gas_ar_shape_full = geom.shapes.Box(self.name + '_gasAr_full_shape',
                                    dx=self.cryo['HeightGaseousAr']/2.0,
                                    dy=self.cryo['Argon_y']/2.0,
                                    dz=self.cryo['Argon_z']/2.0)

        # Get X-ARAPUCA builder and its volume
        xarapuca_builder = self.get_builder('xarapuca')
        arapuca_vol = xarapuca_builder.get_volume('volXARAPUCAWall')  
        window_vol = xarapuca_builder.get_volume('volXARAPUCAWindow')
        arapuca_shape = arapuca_vol.shape

        # Calculate X-ARAPUCA subtraction positions from gas argon
        # First X-ARAPUCA position
        arapuca_pos1 = geom.structure.Position(
            "gasAr_arapuca_pos1",
            x = -0.5*self.cryo['HeightGaseousAr'] - 
                self.cryo['Upper_xLArBuffer'] - 
                self.xarapuca['FirstFrameVertDist'] - 
                self.tpc['ReadoutPlane'],
            y = -self.cathode['widthCathode'] - 
                self.xarapuca['CathodeFrameToFC'] - 
                self.xarapuca['FCToArapucaSpaceLat'],
            z = -0.5*self.cryo['Argon_z'] + 
                self.cryo['zLArBuffer'] + 
                0.5*self.cathode['lengthCathode']
        )

        # Create first subtraction 
        gas_ar_sub1 = geom.shapes.Boolean(
            self.name + '_gasAr_sub1',
            type='subtraction',
            first=gas_ar_shape_full,
            second=arapuca_shape,
            pos=arapuca_pos1
        )

        # Second X-ARAPUCA position (mirrored in Y)
        arapuca_pos2 = geom.structure.Position(
            "gasAr_arapuca_pos2", 
            x = arapuca_pos1.x,
            y = self.cathode['widthCathode'] + 
                self.xarapuca['CathodeFrameToFC'] + 
                self.xarapuca['FCToArapucaSpaceLat'],
            z = arapuca_pos1.z
        )

        # Create final gas argon shape with both subtractions
        gas_ar_shape_final = geom.shapes.Boolean(
            self.name + '_gasAr_final',
            type='subtraction',
            first=gas_ar_sub1,
            second=arapuca_shape,
            pos=arapuca_pos2
        )

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
                                        shape=gas_ar_shape_final)

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


        if self.cathode_switch:
            cathode_builder = self.get_builder('cathode')
            xarapuca_builder = self.get_builder('xarapuca')
        
            if cathode_builder:
                # # Configure cathode builder with xarapuca builder
                # cathode_builder.configure(
                #     cathode_parameters=self.cathode,
                #     tpc_params=self.tpc,
                #     xarapuca_builder=xarapuca_builder,
                #     print_config=self.print_config,
                #     print_construct=self.print_construct
                # )
                
                # Create dictionary of placement parameters
                placement_params = {
                    'HeightGaseousAr': self.cryo['HeightGaseousAr'],
                    'Upper_xLArBuffer': self.cryo['Upper_xLArBuffer'],
                    'driftTPCActive': self.tpc['driftTPCActive'],
                    'ReadoutPlane': self.tpc['ReadoutPlane'],
                    'yLArBuffer': self.cryo['yLArBuffer'],
                    'zLArBuffer': self.cryo['zLArBuffer'],
                    'nCRM_z': self.tpc['nCRM_z'],
                    'nCRM_x': self.tpc['nCRM_x']
                }
                
                # Call placement function
                argon_dim = (self.cryo['Argon_x'], self.cryo['Argon_y'], self.cryo['Argon_z'])
                cathode_builder.place_in_volume(geom, argon_vol, argon_dim, placement_params, xarapuca_builder)

        self.add_volume(cryo_vol)