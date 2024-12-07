#!/usr/bin/env python
'''
Cryostat builder for ProtoDUNE-VD geometry 
'''

import gegede.builder
from gegede import Quantity as Q

class CryostatBuilder(gegede.builder.Builder):
    '''
    Build the ProtoDUNE-VD cryostat
    '''
    
    def configure(self, 
                 Cryostat_x=None, Cryostat_y=None, Cryostat_z=None,  # Overall dimensions
                 SteelThickness=None,                                 # Membrane thickness
                 Argon_x=None, Argon_y=None, Argon_z=None,          # Inner argon volume
                 FieldCage_switch = True, HeightGaseousAr=None,     # Height of gas argon layer
                 Cathode_switch=True, ArapucaMesh_switch=True,
                 driftTPCActive=None,
                 widthTPCActive=None, 
                 lengthTPCActive=None,
                 ReadoutPlane=Q('0.06cm'),  # 3 readout planes of 0.02cm each
                 ArapucaOut_x=None, ArapucaOut_y=None, ArapucaOut_z=None,
                 ArapucaIn_x=None, ArapucaIn_y=None, ArapucaIn_z=None,
                 BeamPlugRad=None, BeamPlugNiRad=None,             # Beam plug parameters
                 BeamPlugUSAr=None, BeamPlugLe=None,               # More beam plug params
                 **kwds):
        
        self.dim = (Cryostat_x, Cryostat_y, Cryostat_z)
        self.steel_thickness = SteelThickness
        self.argon_dim = (Argon_x, Argon_y, Argon_z)
        self.gas_argon_height = HeightGaseousAr
        self.drift_active = driftTPCActive
        self.readout_plane = ReadoutPlane
        self.width_active = widthTPCActive
        self.length_active = lengthTPCActive
        
        # Beam plug parameters
        self.beam_plug = dict(
            rad = BeamPlugRad,
            ni_rad = BeamPlugNiRad,
            us_ar = BeamPlugUSAr,
            length = BeamPlugLe
        )

        self.fieldcage_switch = FieldCage_switch
        self.cathode_on = Cathode_switch
        self.arapuca_mesh_on = ArapucaMesh_switch
        
        # Calculate buffer regions following PERL logic:
        # xLArBuffer = $Argon_x - $driftTPCActive - $HeightGaseousAr - $ReadoutPlane;
        self.xLArBuffer = self.argon_dim[0] - self.drift_active - \
                         self.gas_argon_height - self.readout_plane
        
        # From PERL:
        # $Upper_xLArBuffer = 23.6 - $ReadoutPlane;
        # $Lower_xLArBuffer = 34.7 - $ReadoutPlane;
        self.upper_xLArBuffer = Q('23.6cm') - self.readout_plane
        self.lower_xLArBuffer = Q('34.7cm') - self.readout_plane

        # From PERL:
        # $yLArBuffer = 0.5 * ($Argon_y - $widthTPCActive);
        # $zLArBuffer = 0.5 * ($Argon_z - $lengthTPCActive);
        self.y_lar_buffer = 0.5 * (self.argon_dim[1] - self.width_active)
        self.z_lar_buffer = 0.5 * (self.argon_dim[2] - self.length_active)

        # X-ARAPUCA parameters  
        self.arapuca_out = (ArapucaOut_x, ArapucaOut_y, ArapucaOut_z)
        self.arapuca_in = (ArapucaIn_x, ArapucaIn_y, ArapucaIn_z)
        

    def construct(self, geom):
        # Main cryostat shape
        cryo_shape = geom.shapes.Box(self.name + '_shape', 
                                   dx=self.dim[0]/2.0,
                                   dy=self.dim[1]/2.0,
                                   dz=self.dim[2]/2.0)

        # Inner argon volume shape
        argon_shape = geom.shapes.Box(self.name + '_argon_shape',
                                    dx=self.argon_dim[0]/2.0,
                                    dy=self.argon_dim[1]/2.0,
                                    dz=self.argon_dim[2]/2.0)

        # Gaseous argon layer shape 
        gas_argon_shape = geom.shapes.Box(self.name + '_gas_argon_shape',
                                        dx=self.gas_argon_height/2.0,
                                        dy=self.argon_dim[1]/2.0,
                                        dz=self.argon_dim[2]/2.0)
        
        # Create steel shell by subtracting argon volume from cryostat
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

        gas_argon_vol = geom.structure.Volume(self.name + '_gas_argon_volume',
                                            material='GAr', 
                                            shape=gas_argon_shape)

        # Position gas argon volume in the argon volume
        gas_pos = geom.structure.Position(
            self.name + '_gas_pos',
            x=(self.argon_dim[0]/2.0 - self.gas_argon_height/2.0),
            y=Q('0.0m'), z=Q('0.0m'))
        
        gas_place = geom.structure.Placement(
            self.name + '_gas_place',
            volume=gas_argon_vol,
            pos=gas_pos)
        
        argon_vol.placements.append(gas_place.name)

        # After creating the argon_vol, add field cage components
        if self.fieldcage_switch:
            fc_builder = self.get_builder('fieldcage')
            if fc_builder:
                # Pass cryostat half-width when placing field shapers
                fc_builder._place_field_shapers(geom, argon_vol, self.dim[0]/2.0)

        if self.cathode_on:
            cathode_builder = self.get_builder('cathode')
            if cathode_builder:
                # Create dictionary of placement parameters
                placement_params = {
                    'gas_argon_height': self.gas_argon_height,
                    'upper_xLArBuffer': self.upper_xLArBuffer,
                    'drift_active': self.drift_active,
                    'readout_plane': self.readout_plane,
                    'y_lar_buffer': self.y_lar_buffer,
                    'z_lar_buffer': self.z_lar_buffer
                }
                
                # Call placement function
                cathode_builder.place_in_volume(geom, argon_vol, self.argon_dim, placement_params)

        # Create overall cryostat volume and add steel shell and argon
        cryo_vol = geom.structure.Volume(self.name + '_volume',
                                       material='Air',
                                       shape=cryo_shape)
        
        steel_place = geom.structure.Placement(
            self.name + '_steel_place',
            volume=steel_vol)
        
        argon_place = geom.structure.Placement(
            self.name + '_argon_place', 
            volume=argon_vol)

        cryo_vol.placements.append(steel_place.name)
        cryo_vol.placements.append(argon_place.name)

        self.add_volume(cryo_vol)
