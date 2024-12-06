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
                 MeshInnerStructureLength_vertical = Q('73.5cm'),
                 MeshInnerStructureLength_horizontal = Q('80.9cm'), 
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
        self.mesh_length_v = MeshInnerStructureLength_vertical
        self.mesh_length_h = MeshInnerStructureLength_horizontal
        self.mesh_rod_inner_r = MeshRodInnerRadius
        self.mesh_rod_outer_r = MeshRodOuterRadius
        self.mesh_separation = MeshInnerStructureSeparation
        self.mesh_nbars_v = MeshInnerStructureNumberOfBars_vertical
        self.mesh_nbars_h = MeshInnerStructureNumberOfBars_horizontal

    # After creating the cathode_vol, add the mesh rods:
    def add_mesh_to_void(self, geom, cathode_vol, void_y, void_z, grid_y, grid_z, void_index, mesh_rod_v_vol, mesh_rod_h_vol):
        '''Add vertical and horizontal mesh rods to a single void'''
        
        # Calculate absolute position of void center
        void_center_y = void_y + grid_y
        void_center_z = void_z + grid_z

        # Place vertical rods
        for i in range(self.mesh_nbars_v):
            # Calculate rod position relative to void center
            rod_y = void_center_y - self.void_width/2 + i*self.mesh_separation
            
            place = geom.structure.Placement(
                self.name + f"_vrod_{void_index}_{i}",
                volume=mesh_rod_v_vol,
                pos=geom.structure.Position(
                    self.name + f"_vrod_pos_{void_index}_{i}",
                    x=Q('0cm'),
                    y=rod_y,
                    z=void_center_z
                )
            )
            cathode_vol.placements.append(place.name)

        # Place horizontal rods 
        for i in range(self.mesh_nbars_h):
            # Calculate rod position relative to void center
            rod_z = void_center_z - self.void_length/2 + i*self.mesh_separation

            place = geom.structure.Placement(
                self.name + f"_hrod_{void_index}_{i}",
                volume=mesh_rod_h_vol,
                pos=geom.structure.Position(
                    self.name + f"_hrod_pos_{void_index}_{i}",
                    x=Q('0cm'),
                    y=void_center_y,
                    z=rod_z
                ),
                rot=geom.structure.Rotation(
                    self.name + f"_hrod_rot_{void_index}_{i}",
                    x=Q('90deg')
                )
            )
            cathode_vol.placements.append(place.name)

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

        # Define void positions for 4x4 grid in a single cathode
        void_positions = [
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

        # Create cathode frame by subtracting all voids
        shape = cathode_box
        for i, (void_y, void_z) in enumerate(void_positions):
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

        # # Create the mesh rod shapes
        # mesh_rod_vertical = geom.shapes.Tubs(
        #     self.name+"_mesh_rod_vertical_shape",
        #     rmin=self.mesh_rod_inner_r,
        #     rmax=self.mesh_rod_outer_r,
        #     dz=self.mesh_length_v/2,
        #     sphi=Q('0deg'),
        #     dphi=Q('360deg'))

        # mesh_rod_horizontal = geom.shapes.Tubs(
        #     self.name+"_mesh_rod_horizontal_shape",
        #     rmin=self.mesh_rod_inner_r,
        #     rmax=self.mesh_rod_outer_r,
        #     dz=self.mesh_length_h/2,
        #     sphi=Q('0deg'),
        #     dphi=Q('360deg'))

        # # Create volumes for mesh rods
        # mesh_rod_v_vol = geom.structure.Volume(
        #     self.name+"_mesh_rod_vertical_vol",
        #     material="G10",
        #     shape=mesh_rod_vertical)

        # mesh_rod_h_vol = geom.structure.Volume(
        #     self.name+"_mesh_rod_horizontal_vol",
        #     material="G10",
        #     shape=mesh_rod_horizontal)
        
        # self.add_volume(mesh_rod_v_vol)
        # self.add_volume(mesh_rod_h_vol)

        # # Then in the main construction code:
        # void_index = 0
        # for grid_y, grid_z in grid_positions:
        #     for void_y, void_z in void_positions:
        #         self.add_mesh_to_void(geom, cathode_vol, void_y, void_z, grid_y, grid_z, void_index, mesh_rod_v_vol, mesh_rod_h_vol)
        #         void_index += 1

        # # Place mesh in each void
        # for i, (void_y, void_z) in enumerate(void_positions):
        #     # Place vertical rods
        #     for j in range(self.mesh_nbars_v):
        #         z_pos = void_z - self.void_length/2 + j*self.mesh_separation
        #         place = geom.structure.Placement(
        #             f"{self.name}_vrod_void{i}_rod{j}_place",
        #             volume=mesh_rod_v_vol,
        #             pos=geom.structure.Position(
        #                 f"{self.name}_vrod_void{i}_rod{j}_pos",
        #                 x=Q('0cm'),
        #                 y=void_y,
        #                 z=z_pos))
        #         cathode_vol.placements.append(place.name)

        #     # Place horizontal rods
        #     for j in range(self.mesh_nbars_h):
        #         y_pos = void_y - self.void_width/2 + j*self.mesh_separation
        #         place = geom.structure.Placement(
        #             f"{self.name}_hrod_void{i}_rod{j}_place",
        #             volume=mesh_rod_h_vol,
        #             pos=geom.structure.Position(
        #                 f"{self.name}_hrod_void{i}_rod{j}_pos",
        #                 x=Q('0cm'),
        #                 y=y_pos,
        #                 z=void_z),
        #             rot=geom.structure.Rotation(
        #                 f"{self.name}_hrod_void{i}_rod{j}_rot",
        #                 x=Q('90deg')))
        #         cathode_vol.placements.append(place.name)

        

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

    
