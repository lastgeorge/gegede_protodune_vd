#!/usr/bin/env python
'''
World builder for ProtoDUNE-VD
'''

import gegede.builder
from gegede import Quantity as Q

class SteelSupportBuilder(gegede.builder.Builder):
    '''Build the steel support structure for ProtoDUNE-VD'''
    
    def configure(self, 
                 # Main support dimensions
                 SteelSupport_x = None,
                 SteelSupport_y = None, 
                 SteelSupport_z = None,
                 SteelPlate = None,
                 FoamPadding = None,
                 
                 # Spacing parameters
                 SpaceSteelSupportToWall = None,
                 SpaceSteelSupportToCeiling = None,
                 
                 # Unit box dimensions
                 BoxCentral_x = None,
                 BoxCentral_y = None,
                 BoxCentral_z = None,
                 BoxWall_x = None,
                 BoxWall_y = None,
                 BoxWall_z = None,
                 BoxCutout_x = None,
                 BoxCutout_y = None,
                 BoxCutout_z = None,
                 **kwds):
        
        self.main_dim = (SteelSupport_x, SteelSupport_y, SteelSupport_z)
        self.plate_thickness = SteelPlate
        self.foam_padding = FoamPadding
        self.wall_space = SpaceSteelSupportToWall
        self.ceiling_space = SpaceSteelSupportToCeiling
        
        # Store box dimensions
        self.box_central = (BoxCentral_x, BoxCentral_y, BoxCentral_z)
        self.box_wall = (BoxWall_x, BoxWall_y, BoxWall_z) 
        self.box_cutout = (BoxCutout_x, BoxCutout_y, BoxCutout_z)

    def construct(self, geom):
        '''Construct the steel support structure'''
        
        # Build basic unit shapes
        center_unit = self._build_center_unit(geom)
        wall_unit = self._build_wall_unit(geom)
        
        # Build support sections
        # top_vol = self._build_tb_section(geom, center_unit, wall_unit)
        # us_vol = self._build_us_section(geom, center_unit, wall_unit)
        # lr_vol = self._build_lr_section(geom, center_unit, wall_unit)
        
        # Create main support volume to contain all sections
        main_shape = geom.shapes.Box(
            self.name + '_shape',
            dx=self.main_dim[0]/2.0,
            dy=self.main_dim[1]/2.0,
            dz=self.main_dim[2]/2.0)
        
        main_vol = geom.structure.Volume(
            self.name + '_volume',
            material='AirSteelMixture', 
            shape=main_shape)
        
        # Add section placements
        # self._place_sections(geom, main_vol, top_vol, us_vol, lr_vol)
        
        self.add_volume(main_vol)

    def _build_center_unit(self, geom):
        '''Build central box unit with cutouts'''
        
        # Create outer box
        box = geom.shapes.Box(
            self.name + '_center_box',
            dx=self.box_central[0]/2.0,
            dy=self.box_central[1]/2.0,
            dz=self.box_central[2]/2.0)
            
        # Create cutout box
        cutout = geom.shapes.Box(
            self.name + '_center_cutout',
            dx=self.box_cutout[0]/2.0,
            dy=self.box_cutout[1]/2.0,
            dz=self.box_cutout[2]/2.0)
            
        # Subtract cutout
        unit = geom.shapes.Boolean(
            self.name + '_center_unit',
            type='subtraction',
            first=box,
            second=cutout)
            
        return geom.structure.Volume(
            self.name + '_center_volume',
            material='STEEL_STAINLESS_Fe7Cr2Ni',
            shape=unit)

    def _build_wall_unit(self, geom):
        '''Build wall box unit with cutouts'''
        # Similar to center unit but with wall dimensions
        box = geom.shapes.Box(
            self.name + '_wall_box',
            dx=self.box_wall[0]/2.0,
            dy=self.box_wall[1]/2.0,
            dz=self.box_wall[2]/2.0)
            
        cutout = geom.shapes.Box(
            self.name + '_wall_cutout', 
            dx=self.box_cutout[0]/2.0,
            dy=self.box_cutout[1]/2.0,
            dz=self.box_cutout[2]/2.0)
            
        unit = geom.shapes.Boolean(
            self.name + '_wall_unit',
            type='subtraction',
            first=box,
            second=cutout)
            
        return geom.structure.Volume(
            self.name + '_wall_volume',
            material='STEEL_STAINLESS_Fe7Cr2Ni', 
            shape=unit)

    def _build_tb_section(self, geom, center_unit, wall_unit):
        '''Build top/bottom support section'''
        
        # Create container volume
        shape = geom.shapes.Box(
            self.name + '_tb_shape',
            dx=self.main_dim[0]/2.0,
            dy=self.main_dim[1]/2.0,
            dz=self.main_dim[2]/2.0)
            
        vol = geom.structure.Volume(
            self.name + '_tb_volume',
            material='Air',
            shape=shape)
            
        # Place units in 5x5 grid
        spacing = Q('160cm')  # From PERL spacing
        for i in range(5):
            for j in range(5):
                if i == 2 and j == 2:  # Center position
                    unit = center_unit
                else:
                    unit = wall_unit
                    
                pos = geom.structure.Position(
                    self.name + f'_tb_unit_pos_{i}_{j}',
                    x=spacing * (i-2),
                    y=spacing * (j-2),
                    z=Q('0cm'))
                    
                place = geom.structure.Placement(
                    self.name + f'_tb_unit_place_{i}_{j}',
                    volume=unit,
                    pos=pos)
                    
                vol.placements.append(place.name)
                
        return vol

    def _build_us_section(self, geom, center_unit, wall_unit):
        '''Build upstream/downstream section'''
        # Similar to top/bottom but rotated
        return self._build_tb_section(geom, center_unit, wall_unit)

    def _build_lr_section(self, geom, center_unit, wall_unit):
        '''Build left/right section'''
        # Similar but with different dimensions
        return self._build_tb_section(geom, center_unit, wall_unit) 

    def _place_sections(self, geom, main_vol, top_vol, us_vol, lr_vol):
        '''Place all sections in the main volume'''
        
        # Top placement
        top_pos = geom.structure.Position(
            self.name + '_top_pos',
            x=Q('0cm'),
            y=self.main_dim[1]/2.0 - self.plate_thickness,
            z=Q('0cm'))
            
        top_place = geom.structure.Placement(
            self.name + '_top_place',
            volume=top_vol,
            pos=top_pos)
            
        main_vol.placements.append(top_place.name)
        
        # Bottom placement (inverted top)
        bot_pos = geom.structure.Position(
            self.name + '_bot_pos',
            x=Q('0cm'),
            y=-(self.main_dim[1]/2.0 - self.plate_thickness),
            z=Q('0cm'))
            
        bot_place = geom.structure.Placement(
            self.name + '_bot_place', 
            volume=top_vol,
            pos=bot_pos,
            rot=geom.structure.Rotation(
                self.name + '_bot_rot',
                x=Q('180deg')))
                
        main_vol.placements.append(bot_place.name)
        
        # US/DS placements
        us_pos = geom.structure.Position(
            self.name + '_us_pos',
            x=Q('0cm'),
            y=Q('0cm'), 
            z=self.main_dim[2]/2.0 - self.plate_thickness)
            
        us_place = geom.structure.Placement(
            self.name + '_us_place',
            volume=us_vol,
            pos=us_pos,
            rot=geom.structure.Rotation(
                self.name + '_us_rot',
                y=Q('90deg')))
                
        main_vol.placements.append(us_place.name)
        
        # Left/Right placements  
        lr_pos = geom.structure.Position(
            self.name + '_lr_pos',
            x=self.main_dim[0]/2.0 - self.plate_thickness,
            y=Q('0cm'),
            z=Q('0cm'))
            
        lr_place = geom.structure.Placement(
            self.name + '_lr_place',
            volume=lr_vol, 
            pos=lr_pos,
            rot=geom.structure.Rotation(
                self.name + '_lr_rot',
                z=Q('90deg')))
                
        main_vol.placements.append(lr_place.name)