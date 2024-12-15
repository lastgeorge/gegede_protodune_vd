#!/usr/bin/env python
'''
Cathode builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class CathodeBuilder(gegede.builder.Builder):
    '''Build the cathode structure including mesh'''

    def __init__(self, name):
        super(CathodeBuilder, self).__init__(name)
        self.params = None

    def configure(self, cathode_parameters=None, tpc_params=None,  print_config=False, print_construct=False, **kwargs):
        """Configure the cathode geometry.
        
        Args:
            cathode_parameters (dict): Cathode parameters from config
            tpc_params (dict): TPC parameters from parent builder
            print_config (bool): Whether to print configuration info
            print_construct (bool): Whether to print construction info
            **kwargs: Additional configuration parameters
        """
        if print_config:
            print('Configure Cathode <- Cryostat <- ProtoDUNE-VD <- World')
        # Add guard against double configuration
        # if hasattr(self, '_configured'):
        #     return
            
        # Store cathode params
        if cathode_parameters:
            self.params = cathode_parameters

            # Calculate additional derived parameters
            # Mesh parameters
            self.params['mesh_length'] = self.params['lengthCathodeVoid'] 
            self.params['mesh_width'] = self.params['widthCathodeVoid']

            # Define void positions for 4x4 grid in a single cathode
            self.params['void_positions'] = []
            
            # Calculate void positions
            for i in range(4):  # rows
                for j in range(4):  # columns
                    # Calculate x position
                    x = (i - 1.5) * self.params['widthCathodeVoid'] + \
                        (i - 2) * self.params['CathodeBorder']
                    
                    # Calculate z position    
                    z = (j - 1.5) * self.params['lengthCathodeVoid'] + \
                        (j - 2) * self.params['CathodeBorder']
                    
                    self.params['void_positions'].append([x, z])
        
        # Store TPC params we need
        if tpc_params:
            # Set width and length based on CRP dimensions
            self.params['widthCathode'] = tpc_params['widthCRP']
            self.params['lengthCathode'] = tpc_params['lengthCRP']
            
            # Set mesh dimensions based on void dimensions
            self.params['CathodeMeshInnerStructureLength_vertical'] = \
                self.params['lengthCathodeVoid']
            self.params['CathodeMeshInnerStructureLength_horizontal'] = \
                self.params['widthCathodeVoid']

        # Update with any overrides from kwargs
        if kwargs:
            self.params.update(kwargs)
            
        # Mark as configured
        # self._configured = True
        self.print_construct = print_construct

    def construct(self, geom):
        '''Construct cathode geometry'''
        if self.print_construct:
            print('Construct Cathode <- Cryostat <- ProtoDUNE-VD <- World')
            
        # Create base cathode box 
        cathode_box = geom.shapes.Box(
            self.name + "_box",
            dx=self.params['heightCathode']/2,
            dy=self.params['widthCathode']/2,     
            dz=self.params['lengthCathode']/2) 

        # Create void box for subtraction
        void_box = geom.shapes.Box(
            self.name + "_void",
            dx=self.params['heightCathode']/2 + Q('0.5cm'),
            dy=self.params['widthCathodeVoid']/2,
            dz=self.params['lengthCathodeVoid']/2)

        # Create cathode frame by subtracting all voids
        shape = cathode_box
        for i, (void_y, void_z) in enumerate(self.params['void_positions']):
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

        # Add main volume to builder
        self.add_volume(cathode_vol)

        # Create mesh rod shapes
        mesh_rod_vertical = geom.shapes.Box(
            self.name+"_mesh_rod_vertical",
            dx=self.params['CathodeMeshInnerStructureThickness'],  # Thickness
            dy=self.params['CathodeMeshInnerStructureWidth'],  # Width
            dz=self.params['mesh_length']/2)  # Length

        # Build complete mesh starting with first vertical rod
        mesh_shape = mesh_rod_vertical
            
        # Add remaining vertical rods
        for i in range(1, self.params['CathodeMeshInnerStructureNumberOfStrips_vertical']):
            pos_y = i*self.params['CathodeMeshInnerStructureSeparation'] 
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

        # Create horizontal rod shape
        mesh_rod_horizontal = geom.shapes.Box(
            self.name+"_mesh_rod_horizontal", 
            dx=self.params['CathodeMeshInnerStructureThickness'],  # Thickness
            dy=self.params['mesh_width']/2,  # Width
            dz=self.params['CathodeMeshInnerStructureWidth'])  # Height

        # Add horizontal rods
        for i in range(self.params['CathodeMeshInnerStructureNumberOfStrips_horizontal']):
            pos_z = -self.params['mesh_length']/2 + (i+1)*self.params['CathodeMeshInnerStructureSeparation']
            mesh_shape = geom.shapes.Boolean(
                self.name + f"_mesh_h{i}",
                type='union',
                first=mesh_shape, 
                second=mesh_rod_horizontal,
                pos=geom.structure.Position(
                    self.name + f"_hrod_pos{i}",
                    x=Q('0cm'),
                    y=self.params['mesh_width']/2-self.params['CathodeMeshInnerStructureSeparation'],
                    z=pos_z
                )
            )

        # Create volume for complete mesh
        mesh_vol = geom.structure.Volume(
            self.name+"_mesh_vol",
            material="G10", 
            shape=mesh_shape)

        # Store mesh volume and add to builder
        self.mesh_vol = mesh_vol
        self.add_volume(mesh_vol)

    def place_in_volume(self, geom, volume, argon_dim, params, xarapuca_builder=None):
        '''Place cathode modules and associated X-ARAPUCAs in the given volume
        
        Args:
            geom: Geometry object 
            volume: Volume to place cathodes in
            argon_dim: Tuple of LAr dimensions (x,y,z)
            params: Dict containing placement parameters
        '''
        
        # Calculate base position
        cathode_x = argon_dim[0]/2 - params['HeightGaseousAr'] - \
                    params['Upper_xLArBuffer'] - \
                    (params['driftTPCActive'] + params['ReadoutPlane']) - \
                    self.params['heightCathode']/2
                    
        base_y = -argon_dim[1]/2 + params['yLArBuffer'] + self.params['widthCathode']/2  
        base_z = -argon_dim[2]/2 + params['zLArBuffer'] + self.params['lengthCathode']/2 
        

        # print(argon_dim[0], argon_dim[1], argon_dim[2])
        # print(-argon_dim[1]/2, params['yLArBuffer'], self.params['widthCathode']/2)
        # print(-argon_dim[2]/2, params['zLArBuffer'], self.params['lengthCathode']/2)

        cathode_vol = self.get_volume()
        mesh_vol = self.mesh_vol

        # Get CRM dimensions from params 
        n_crm_z = params.get('nCRM_z', 4)  # Default 4 if not specified
        n_crm_x = params.get('nCRM_x', 4)  # Default 4 if not specified

        # Get X-ARAPUCA volumes if builder is available
        arapuca_wall = None
        if xarapuca_builder:
            arapuca_wall = xarapuca_builder.get_volume('volXARAPUCAWall')
            arapuca_window = xarapuca_builder.get_volume('volXARAPUCAWindow')

        # Place cathodes and meshes in 2x2 grid
        for i in range(n_crm_x//2):  # y direction
            for j in range(n_crm_z//2):  # z direction
                # Calculate center position of this cathode module
                module_x = cathode_x
                module_y = base_y + i*self.params['widthCathode']
                module_z = base_z + j*self.params['lengthCathode']

                # Place cathode frame
                pos = geom.structure.Position(
                    f"{self.name}_pos_{i}_{j}",
                    x=module_x,
                    y=module_y,
                    z=module_z
                )
                
                place = geom.structure.Placement(
                    f"{self.name}_place_{i}_{j}",
                    volume=cathode_vol,
                    pos=pos
                )
                
                volume.placements.append(place.name)

                # Place X-ARAPUCAs associated with this cathode module
                if xarapuca_builder and arapuca_wall:
                    # Get the predefined rotation from geometry object
                    # rot = geom.structure.getRotation('rPlus90AboutXPlus90AboutZ')
                    
                    # Calculate X-ARAPUCA positions relative to this cathode module
                    arapuca_positions = xarapuca_builder.calculate_cathode_positions(
                        module_x, module_y, module_z
                    )
                    
                    # Place each X-ARAPUCA with rotation
                    for idx, (x, y, z) in enumerate(arapuca_positions):
                        print (idx, x, y, z)
                        arapuca_pos = geom.structure.Position(
                            f"pos_cathode_{i}_{j}_xarapuca_{idx}",
                            x=x, y=y, z=z
                        )
                        
                        # Include rotation in placement
                        arapuca_place = geom.structure.Placement(
                            f"place_cathode_{i}_{j}_xarapuca_{idx}",
                            volume=arapuca_wall,
                            pos=arapuca_pos,
                            rot='rPlus90AboutXPlus90AboutZ'    # Add rotation here
                        )
                        
                        volume.placements.append(arapuca_place.name)

                # Place mesh in each void position
                for void_idx, (void_y, void_z) in enumerate(self.params['void_positions']):
                    mesh_pos = geom.structure.Position(
                        f"{self.name}_mesh_pos_{i}_{j}_{void_idx}",
                        x=cathode_x,
                        y=base_y + i*self.params['widthCathode'] + void_y - \
                        self.params['mesh_width']/2 + self.params['CathodeMeshInnerStructureSeparation'],
                        z=base_z + j*self.params['lengthCathode'] + void_z
                    )
                    
                    mesh_place = geom.structure.Placement(
                        f"{self.name}_mesh_place_{i}_{j}_{void_idx}",
                        volume=mesh_vol,
                        pos=mesh_pos
                    )
                    
                    volume.placements.append(mesh_place.name)