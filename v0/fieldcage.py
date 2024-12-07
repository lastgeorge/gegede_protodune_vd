#!/usr/bin/env python
'''
Field Cage builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class FieldCageBuilder(gegede.builder.Builder):
    '''
    Build the field cage for ProtoDUNE-VD.
    Implements both thick and slim field shapers arranged vertically.
    '''
    
    def configure(self, 
                 # Field shaper dimensions
                 FieldShaperInnerRadius = Q('1.758cm'),
                 FieldShaperOuterRadius = Q('1.858cm'),
                 FieldShaperSlimInnerRadius = Q('0.65cm'),
                 FieldShaperSlimOuterRadius = Q('0.80cm'),
                 FieldShaperTorRad = Q('10cm'),
                 FieldShaperLength = Q('329.4cm'),
                 FieldShaperWidth = Q('704.5cm'),
                 FieldShaperSeparation = Q('6.0cm'),
                 NFieldShapers = 114,
                 FirstFieldShaper_to_MembraneRoof = Q('76cm'),
                 **kwds):
        
        self.inner_radius = FieldShaperInnerRadius
        self.outer_radius = FieldShaperOuterRadius
        self.slim_inner_radius = FieldShaperSlimInnerRadius
        self.slim_outer_radius = FieldShaperSlimOuterRadius
        self.tor_radius = FieldShaperTorRad
        
        # Adjust length and width to account for corner radius
        self.length = FieldShaperLength - 2*FieldShaperTorRad
        self.width = FieldShaperWidth - 2*FieldShaperTorRad
        
        self.separation = FieldShaperSeparation
        self.n_shapers = NFieldShapers
        self.first_to_roof = FirstFieldShaper_to_MembraneRoof

    def construct(self, geom):
        '''Construct the field cage geometry'''
        self._build_field_shaper_shapes(geom)
        self._build_volumes(geom)

        # Create volume for thick field shapers
        thick_vol = geom.structure.Volume(
            self.name + '_thick_volume',
            material = 'Aluminum',
            shape = self.thick_shape)
            
        # Create volume for slim field shapers  
        slim_vol = geom.structure.Volume(
            self.name + '_slim_volume',
            material = 'Aluminum', 
            shape = self.slim_shape)

        # Add both volumes
        self.add_volume(slim_vol)
        self.add_volume(thick_vol)
        
    def _build_field_shaper_shapes(self, geom):
        '''Create the shapes for thick and slim field shapers'''
        
        # Create corner torus for thick field shaper
        self.corner_shape = geom.shapes.Torus(
            self.name + '_corner',
            rmin = self.inner_radius,
            rmax = self.outer_radius,
            rtor = self.tor_radius,
            startphi = Q('0deg'),
            deltaphi = Q('90deg'))
            
        # Create corner torus for slim field shaper
        self.slim_corner_shape = geom.shapes.Torus(
            self.name + '_slim_corner',
            rmin = self.slim_inner_radius,
            rmax = self.slim_outer_radius,
            rtor = self.tor_radius,
            startphi = Q('0deg'),
            deltaphi = Q('90deg'))
            
        # Create straight sections
        self.straight_shape = geom.shapes.Box(
            self.name + '_straight',
            dx = self.outer_radius,
            dy = self.length/2,
            dz = self.width/2)
            
        self.slim_straight_shape = geom.shapes.Box(
            self.name + '_slim_straight',
            dx = self.slim_outer_radius,
            dy = self.length/2,
            dz = self.width/2)
            
        # Build complete field shaper shapes through unions
        self._build_complete_shapes(geom)

    def _build_complete_shapes(self, geom):
        '''Build complete field shaper shapes using boolean operations'''
    
        # Start with straight sections for thick field shaper
        self.thick_shape = self.straight_shape

        # Add first corner
        fs_union1 = geom.shapes.Boolean(
            self.name + '_union1',
            type = 'union',
            first = self.thick_shape,
            second = self.corner_shape,
            pos = geom.structure.Position(
                self.name + '_corn1_pos',
                x = Q('0cm'),
                y = self.length/2,
                z = -self.width/2))
                
        # Update shape
        self.thick_shape = fs_union1
            
        # Add second corner
        fs_union2 = geom.shapes.Boolean(
            self.name + '_union2', 
            type = 'union',
            first = self.thick_shape,
            second = self.corner_shape,
            pos = geom.structure.Position(
                self.name + '_corn2_pos',
                x = Q('0cm'), 
                y = -self.length/2,
                z = -self.width/2),
            rot = geom.structure.Rotation(
                self.name + '_rot2',
                x = Q('90deg')))
                
        self.thick_shape = fs_union2

        # Similarly for slim field shapers
        self.slim_shape = self.slim_straight_shape
        
        slim_union1 = geom.shapes.Boolean(
            self.name + '_slim_union1',
            type = 'union', 
            first = self.slim_shape,
            second = self.slim_corner_shape,
            pos = geom.structure.Position(
                self.name + '_slim_corn1_pos',
                x = Q('0cm'),
                y = self.length/2,
                z = -self.width/2))
                
        self.slim_shape = slim_union1
        
        slim_union2 = geom.shapes.Boolean(
            self.name + '_slim_union2',
            type = 'union',
            first = self.slim_shape, 
            second = self.slim_corner_shape,
            pos = geom.structure.Position(
                self.name + '_slim_corn2_pos',
                x = Q('0cm'),
                y = -self.length/2, 
                z = -self.width/2),
            rot = geom.structure.Rotation(
                self.name + '_slim_rot2',
                x = Q('90deg')))
                
        self.slim_shape = slim_union2

    def _build_volumes(self, geom):
        '''Create volumes for field shapers'''
        
        # Volume for thick field shapers
        self.thick_vol = geom.structure.Volume(
            self.name + '_thick_vol',
            material = 'Aluminum',
            shape = self.thick_shape)
            
        # Volume for slim field shapers
        self.slim_vol = geom.structure.Volume(
            self.name + '_slim_vol',
            material = 'Aluminum',
            shape = self.slim_shape)
            
        # Add both volumes
        self.add_volume(self.thick_vol)
        self.add_volume(self.slim_vol)

    def _place_field_shapers(self, geom, lar_volume, cryo_halfwidth):
        '''Place all field shapers in the LAr volume'''
        
        # Calculate starting position including cryostat offset
        start_x = cryo_halfwidth - self.first_to_roof
        
        # Place field shapers
        for i in range(self.n_shapers):
            x_pos = start_x - i * self.separation
            
            # First 36 and last 36 are slim, middle 42 are thick
            is_slim = (i < 36) or (i > 77)
            vol = self.slim_vol if is_slim else self.thick_vol
            
            # Create placement
            pos = geom.structure.Position(
                f"{self.name}_fs{i}_pos",
                 # Use Q() with proper unit strings
                x = Q(f"{x_pos}") if isinstance(x_pos, (int, float)) else x_pos,
                y = Q("0cm"),
                z = Q("0cm"))
                
            rot = geom.structure.Rotation(
                f"{self.name}_fs{i}_rot",
                x = Q("90deg"),
                y = Q("0deg"),
                z = Q("0deg"))
                
            place = geom.structure.Placement(
                f"{self.name}_fs{i}_place",
                volume = vol,
                pos = pos,
                rot = rot)
            
            # Add placement to the LAr volume
            lar_volume.placements.append(place.name)
