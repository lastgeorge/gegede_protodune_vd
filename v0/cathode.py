#!/usr/bin/env python
'''
Cathode builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class CathodeBuilder(gegede.builder.Builder):
    '''Build the cathode structure including mesh'''
    
    def configure(self, 
                 heightCathode = Q('6.0cm'),
                 widthCathode = Q('337.0cm'),
                 lengthCathode = Q('299.3cm'),
                 CathodeBorder = Q('4.0cm'),
                 widthCathodeVoid = Q('77.25cm'),
                 lengthCathodeVoid = Q('67.25cm'),
                 # Mesh parameters
                 MeshRodInnerRadius = Q('0cm'),
                 MeshRodOuterRadius = Q('0.1cm'),
                 MeshInnerStructureSeparation = Q('2.5cm'),
                 MeshInnerStructureNumberOfBars_vertical = 30,
                 MeshInnerStructureNumberOfBars_horizontal = 26,
                 **kwds):
        
        self.height = heightCathode
        self.width = widthCathode
        self.length = lengthCathode
        self.border = CathodeBorder
        self.void_width = widthCathodeVoid
        self.void_length = lengthCathodeVoid
        
        # Mesh parameters
        self.mesh_length = self.void_length
        self.mesh_width = self.void_width
        self.mesh_rod_inner_r = MeshRodInnerRadius
        self.mesh_rod_outer_r = MeshRodOuterRadius
        self.mesh_separation = MeshInnerStructureSeparation
        self.mesh_nbars_v = MeshInnerStructureNumberOfBars_vertical
        self.mesh_nbars_h = MeshInnerStructureNumberOfBars_horizontal

        # Define void positions for 4x4 grid in a single cathode
        self.void_positions = [
            # First row (bottom)
            [-1.5*self.void_width-2.0*self.border, -1.5*self.void_length-2.0*self.border],
            [-1.5*self.void_width-2.0*self.border, -0.5*self.void_length-1.0*self.border],
            [-1.5*self.void_width-2.0*self.border, 0.5*self.void_length+1.0*self.border],
            [-1.5*self.void_width-2.0*self.border, 1.5*self.void_length+2.0*self.border],
            # Second row 
            [-0.5*self.void_width-1.0*self.border, -1.5*self.void_length-2.0*self.border],
            [-0.5*self.void_width-1.0*self.border, -0.5*self.void_length-1.0*self.border],
            [-0.5*self.void_width-1.0*self.border, 0.5*self.void_length+1.0*self.border],
            [-0.5*self.void_width-1.0*self.border, 1.5*self.void_length+2.0*self.border],
            # Third row
            [0.5*self.void_width+1.0*self.border, -1.5*self.void_length-2.0*self.border],
            [0.5*self.void_width+1.0*self.border, -0.5*self.void_length-1.0*self.border],
            [0.5*self.void_width+1.0*self.border, 0.5*self.void_length+1.0*self.border],
            [0.5*self.void_width+1.0*self.border, 1.5*self.void_length+2.0*self.border],
            # Fourth row (top)
            [1.5*self.void_width+2.0*self.border, -1.5*self.void_length-2.0*self.border],
            [1.5*self.void_width+2.0*self.border, -0.5*self.void_length-1.0*self.border],
            [1.5*self.void_width+2.0*self.border, 0.5*self.void_length+1.0*self.border],
            [1.5*self.void_width+2.0*self.border, 1.5*self.void_length+2.0*self.border]
        ]


    def construct(self, geom):
        '''Construct cathode following exact PERL script logic'''
        
        # Create base cathode box 
        cathode_box = geom.shapes.Box(
            self.name + "_box",
            dx=self.height/2,
            dy=self.width/2,     
            dz=self.length/2) 

        # Create void box for subtraction
        void_box = geom.shapes.Box(
            self.name + "_void",
            dx=self.height/2 + Q('0.5cm'),
            dy=self.void_width/2,
            dz=self.void_length/2)

        

        # Create cathode frame by subtracting all voids
        shape = cathode_box
        for i, (void_y, void_z) in enumerate(self.void_positions):
            shape = geom.shapes.Boolean(
                self.name + f"_shape{i+1}",
                type='subtraction',
                first=shape,
                second=void_box,
                pos=geom.structure.Position(
                    self.name + f"_void_pos{i+1}",
                    x=Q('0cm'),
                    y=void_y,
                    z=void_z))

        # Create main cathode volume with G10 material
        cathode_vol = geom.structure.Volume(
            self.name+"_volume", 
            material="G10",
            shape=shape)

        # Add all volumes to builder
        self.add_volume(cathode_vol)

        # Create mesh rod shapes
        mesh_rod_vertical = geom.shapes.Box(
            self.name+"_mesh_rod_vertical",
            dx=Q('0.05cm'),  # Thickness
            dy=Q('0.25cm'),
            dz=self.mesh_length/2)  # Width

        # Build complete mesh by unioning rods
        # Start with first vertical rod
        mesh_shape = mesh_rod_vertical
        
        # Add remaining vertical rods
        for i in range(1, self.mesh_nbars_v):
            pos_y = i*self.mesh_separation
            mesh_shape = geom.shapes.Boolean(
            self.name + f"_mesh_v{i}",
            type='union',
            first=mesh_shape,
            second=mesh_rod_vertical,
            pos=geom.structure.Position(
                self.name + f"_vrod_pos{i}",
                x=Q('0cm'),
                y=pos_y,
                z=Q('0cm'))
            )

        

        mesh_rod_horizontal = geom.shapes.Box(
            self.name+"_mesh_rod_horizontal", 
            dx=Q('0.05cm'),  # Thickness
            dy=self.mesh_width/2,  # Width
            dz=Q('0.25cm'))

        # Add horizontal rods
        for i in range(self.mesh_nbars_h):
            pos_z = -self.mesh_length/2 + (i+1)*self.mesh_separation
            mesh_shape = geom.shapes.Boolean(
                self.name + f"_mesh_h{i}",
                type='union',
                first=mesh_shape, 
                second=mesh_rod_horizontal,
                pos=geom.structure.Position(
                    self.name + f"_hrod_pos{i}",
                    x=Q('0cm'),
                    y=self.mesh_width/2-self.mesh_separation,
                    z=pos_z
                )
            )

        # Create volume for complete mesh
        mesh_vol = geom.structure.Volume(
            self.name+"_mesh_vol",
            material="G10",
            shape=mesh_shape)

        # Store mesh volume for placement
        self.mesh_vol = mesh_vol
        self.add_volume(mesh_vol)

        

    def place_in_volume(self, geom, volume, argon_dim, params):
        '''Place cathode modules in the given volume (typically LAr volume)
        
        Args:
            geom: Geometry object
            volume: Volume to place cathodes in
            argon_dim: Tuple of LAr dimensions (x,y,z)
            params: Dict containing placement parameters:
                - gas_argon_height
                - upper_xLArBuffer
                - drift_active
                - readout_plane
                - y_lar_buffer
                - z_lar_buffer
        '''
        
        # Calculate base position for first cathode
        cathode_x = argon_dim[0]/2 - params['gas_argon_height'] - \
                    params['upper_xLArBuffer'] - \
                    (params['drift_active'] + params['readout_plane']) - \
                    self.height/2
                    
        base_y = -argon_dim[1]/2 + params['y_lar_buffer'] + self.width/2
        base_z = -argon_dim[2]/2 + params['z_lar_buffer'] + self.length/2
        
        cathode_vol = self.get_volume()
        mesh_vol = self.mesh_vol

        # Place in 2x2 grid
        for i in range(2):  # y direction
            for j in range(2):  # z direction
                pos = geom.structure.Position(
                    f"{self.name}_pos_{i}_{j}",
                    x=cathode_x,
                    y=base_y + i*self.width,  # Shift by half width each time
                    z=base_z + j*self.length   # Shift by half length each time
                )
                
                place = geom.structure.Placement(
                    f"{self.name}_place_{i}_{j}",
                    volume=cathode_vol,
                    pos=pos
                )
                
                volume.placements.append(place.name)

                # Place mesh in each void position
                for void_idx, (void_y, void_z) in enumerate(self.void_positions):
                    # Calculate absolute position for mesh
                    mesh_pos = geom.structure.Position(
                        f"{self.name}_mesh_pos_{i}_{j}_{void_idx}",
                        x=cathode_x,
                        y=base_y + i*self.width + void_y-self.mesh_width/2+self.mesh_separation,
                        z=base_z + j*self.length + void_z
                    )
                    
                    mesh_place = geom.structure.Placement(
                        f"{self.name}_mesh_place_{i}_{j}_{void_idx}",
                        volume=mesh_vol,
                        pos=mesh_pos
                    )
                    
                    volume.placements.append(mesh_place.name)
                    
