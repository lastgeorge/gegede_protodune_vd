#!/usr/bin/env python
'''
xarapuca builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class XARAPUCABuilder(gegede.builder.Builder):
    '''
    Build the Xarapucas for ProtoDUNE-VD.
    '''

    def __init__(self, name):
        super(XARAPUCABuilder, self).__init__(name)
        self.params = None
        self.cathode = None

    def configure(self, xarapuca_parameters=None, cathode_parameters=None, print_config=False, print_construct=False, **kwargs):
        """Configure the X-ARAPUCA geometry.
        
        Args:
            xarapuca_parameters: Dictionary containing X-ARAPUCA parameters
            cathode_parameters: Dictionary containing cathode parameters
            print_config: Whether to print configuration info
            print_construct: Whether to print construct info
            **kwargs: Additional configuration parameters
        """
        if print_config:
            print('Configure XARAPUCA <- Cryostat <- ProtoDUNE-VD <- World')
        if hasattr(self, '_configured'):
            return
        
        # Store parameters
        if xarapuca_parameters:
            self.params = xarapuca_parameters
        if cathode_parameters:
            self.cathode = cathode_parameters

        self.print_construct = print_construct

        # Calculate additional parameters
        if self.params and self.cathode:
            
            
            # Calculate positions of the 4 arapucas with respect to the Frame center
            self.list_posx_bot = []
            self.list_posz_bot = []
            
            # First arapuca
            self.list_posx_bot.append(-2*self.cathode['widthCathodeVoid'] - 
                                    2.0*self.cathode['CathodeBorder'] + 
                                    self.params['GapPD'] + 
                                    0.5*self.params['ArapucaOut_x'])
            self.list_posz_bot.append(0.5*self.cathode['lengthCathodeVoid'] + 
                                    self.cathode['CathodeBorder'])
            
            # Second arapuca
            self.list_posx_bot.append(-self.cathode['CathodeBorder'] - 
                                    self.params['GapPD'] - 
                                    0.5*self.params['ArapucaOut_x'])
            self.list_posz_bot.append(-1.5*self.cathode['lengthCathodeVoid'] - 
                                    2.0*self.cathode['CathodeBorder'])
            
            # Third arapuca (mirror of second)
            self.list_posx_bot.append(-self.list_posx_bot[1])
            self.list_posz_bot.append(-self.list_posz_bot[1])
            
            # Fourth arapuca (mirror of first)
            self.list_posx_bot.append(-self.list_posx_bot[0])
            self.list_posz_bot.append(-self.list_posz_bot[0])

        if self.params:
            # Calculate derived mesh parameters
            self.params['MeshInnerStructureSeparation'] = (
                self.params['MeshInnerStructureSeparation_base'] + 
                self.params['MeshRodOuterRadius']
            )
            
            # Calculate number of mesh bars for cathode X-ARAPUCA
            if self.cathode:
                self.params['CathodeArapucaMeshNumberOfBars_vertical'] = int(
                    self.cathode['lengthCathodeVoid'] / 
                    self.params['CathodeArapucaMeshRodSeparation']
                )
                self.params['CathodeArapucaMeshNumberOfBars_horizontal'] = int(
                    self.cathode['widthCathodeVoid'] / 
                    self.params['CathodeArapucaMeshRodSeparation']
                )

            # Calculate distance between mesh and window
            self.params['Distance_Mesh_Window'] = Q('1.8cm') + self.params['MeshOuterRadius']

        self._configured = True

    def construct_cathode_mesh(self, geom):
        """Construct mesh for double-sided cathode X-ARAPUCAs"""
        

        # Create outer module box to contain the mesh
        module_shape = geom.shapes.Box(
            "CathodeArapucaMeshModule",
            dx=2*self.params['CathodeArapucaMeshRodRadius'],
            dy=self.cathode['widthCathodeVoid']/2.,
            dz=self.cathode['lengthCathodeVoid']/2.
        )

        # Create vertical rod shape
        vert_rod = geom.shapes.Tubs(
            "CathodeArapucaMeshRod_vertical",
            rmin=Q('0cm'),
            rmax=self.params['CathodeArapucaMeshRodRadius'],
            dz=self.cathode['widthCathodeVoid']/2.
        )

        # Create horizontal rod shape
        horiz_rod = geom.shapes.Tubs(
            "CathodeArapucaMeshRod_horizontal",
            rmin=Q('0cm'),
            rmax=self.params['CathodeArapucaMeshRodRadius'], 
            dz=self.cathode['lengthCathodeVoid']/2.,
        )

        # Create volume for module
        mesh_vol = geom.structure.Volume(
            "volCathodeArapucaMesh",
            material="LAr",
            shape=module_shape
        )

        # print(int(self.params['CathodeArapucaMeshNumberOfBars_vertical']),int(self.params['CathodeArapucaMeshNumberOfBars_horizontal']))

        # Add vertical rods
        n_vert = int(self.params['CathodeArapucaMeshNumberOfBars_vertical'])
        for i in range(n_vert):
            # Create volume for vertical rod
            vert_rod_vol = geom.structure.Volume(
                f"volCathodeArapucaMeshRod_vertical_{i}",
                material="STEEL_STAINLESS_Fe7Cr2Ni",
                shape=vert_rod
            )
            
            # Place vertical rod in module
            pos = geom.structure.Position(
                f"posCathodeMeshRod_vertical{i}",
                x=-(self.params['CathodeArapucaMeshRodRadius']),
                y=Q('0cm'),
                z=-self.cathode['lengthCathodeVoid']/2 + \
                self.params['CathodeArapucaMesh_verticalOffset'] + \
                i*self.params['CathodeArapucaMeshRodSeparation']
            )
            
            place = geom.structure.Placement(
                f"placeCathodeMeshRod_vertical{i}",
                volume=vert_rod_vol,
                pos=pos,
                rot='rPlus90AboutX'
            )
            mesh_vol.placements.append(place.name)

        # Add horizontal rods  
        n_horiz = int(self.params['CathodeArapucaMeshNumberOfBars_horizontal'])
        for i in range(n_horiz):
            # Create volume for horizontal rod
            horiz_rod_vol = geom.structure.Volume(
                f"volCathodeArapucaMeshRod_horizontal_{i}",
                material="STEEL_STAINLESS_Fe7Cr2Ni", 
                shape=horiz_rod
            )

            # Place horizontal rod in module
            pos = geom.structure.Position(
                f"posCathodeMeshRod_horizontal{i}",
                x=(self.params['CathodeArapucaMeshRodRadius']),
                y=-self.cathode['widthCathodeVoid']/2 + \
                self.params['CathodeArapucaMesh_horizontalOffset'] + \
                i*self.params['CathodeArapucaMeshRodSeparation'],
                z=Q('0cm')
            )

            place = geom.structure.Placement(
                f"placeCathodeMeshRod_horizontal{i}",
                volume=horiz_rod_vol,
                pos=pos,
            )
            mesh_vol.placements.append(place.name)

        self.add_volume(mesh_vol)
        return mesh_vol


        # # Create vertical rod shape
        # vert_rod = geom.shapes.Tubs(
        #     f"{self.name}_cathode_xarapuca_vert_rod",  # Make name unique
        #     rmin = Q('0cm'),
        #     rmax=self.params['CathodeArapucaMeshRodRadius'],
        #     dz=self.params['MeshTubeLength_vertical']/2.
        # )
        
        # # Create horizontal rod shape  
        # horiz_rod = geom.shapes.Tubs(
        #     f"{self.name}_cathode_xarapuca_horiz_rod",  # Make name unique
        #     rmin = Q('0cm'),
        #     rmax=self.params['CathodeArapucaMeshRodRadius'],
        #     dz=self.params['MeshTubeLength_horizontal']/2.
        # )

        # # Build mesh starting with first vertical rod
        # mesh_shape = vert_rod
        
        # # Add remaining vertical rods
        # for i in range(1, self.params['CathodeArapucaMeshNumberOfBars_vertical']):
        #     pos_y = i * self.params['CathodeArapucaMeshRodSeparation'] #+ self.params['CathodeArapucaMesh_verticalOffset']
        #     mesh_shape = geom.shapes.Boolean(
        #         f"{self.name}_cathode_mesh_v{i}",  # Make name unique
        #         type='union',
        #         first=mesh_shape,
        #         second=vert_rod,
        #         pos=geom.structure.Position(
        #             f"{self.name}_cathode_vrod_pos{i}",  # Make name unique
        #             x=Q('0cm'),
        #             y=pos_y, 
        #             z=Q('0cm')
        #         )
        #     )

        # # Add horizontal rods
        # for i in range(self.params['CathodeArapucaMeshNumberOfBars_horizontal']):
        #     pos_z = i * self.params['CathodeArapucaMeshRodSeparation']  - self.cathode['lengthCathodeVoid']/2. #+ self.params['CathodeArapucaMesh_horizontalOffset']
        #     mesh_shape = geom.shapes.Boolean(
        #         f"{self.name}_cathode_mesh_h{i}",  # Make name unique
        #         type='union',
        #         first=mesh_shape,
        #         second=horiz_rod,
        #         pos=geom.structure.Position(
        #             f"{self.name}_cathode_hrod_pos{i}",  # Make name unique
        #             x=Q('0cm'),
        #             y=self.cathode['widthCathodeVoid']/2. - self.params['CathodeArapucaMeshRodSeparation'],
        #             z=pos_z,
        #         ),
        #         rot='rPlus90AboutX'
        #     )

        # # Create volume for complete mesh
        # mesh_vol = geom.structure.Volume(
        #     f"{self.name}_volCathodeXarapucaMesh",  # Make name unique
        #     material="STEEL_STAINLESS_Fe7Cr2Ni",
        #     shape=mesh_shape
        # )
        
        # # print(f"Adding volume {mesh_vol.name} to builder")

        self.add_volume(mesh_vol)
        return mesh_vol


    def construct(self, geom):
        """Construct the X-ARAPUCA geometry."""
        if self.print_construct:
            print('Construct XARAPUCA <- Cryostat <- ProtoDUNE-VD <- World')
    
        # Regular ARAPUCA shapes
        out_box = geom.shapes.Box("XARAPUCA_out_shape",
                                dx=self.params['ArapucaOut_x']/2.0,
                                dy=self.params['ArapucaOut_y']/2.0,
                                dz=self.params['ArapucaOut_z']/2.0)

        in_box = geom.shapes.Box("XARAPUCA_in_shape", 
                            dx=self.params['ArapucaIn_x']/2.0,
                            dy=self.params['ArapucaOut_y']/2.0,  # Note: Uses ArapucaOut_y
                            dz=self.params['ArapucaIn_z']/2.0)

        # Regular ARAPUCA walls - subtraction with offset
        wall_shape = geom.shapes.Boolean("XARAPUCA_wall_shape",
                        type='subtraction',
                        first=out_box,
                        second=in_box,
                        pos=geom.structure.Position(
                            "posArapucaSub",
                            x=Q('0cm'),
                            y=self.params['ArapucaOut_y']/2.0,
                            z=Q('0cm')))

        # Regular acceptance window
        window_shape = geom.shapes.Box("XARAPUCA_window_shape",
                                    dx=self.params['ArapucaAcceptanceWindow_x']/2.0,
                                    dy=self.params['ArapucaAcceptanceWindow_y']/2.0,
                                    dz=self.params['ArapucaAcceptanceWindow_z']/2.0)
    


        # Double ARAPUCA shapes
        double_in_box = geom.shapes.Box("XARAPUCA_double_in_shape",
                                    dx=self.params['ArapucaIn_x']/2.0,
                                    dy=(self.params['ArapucaOut_y'] + Q('1.0cm'))/2.0,
                                    dz=self.params['ArapucaIn_z']/2.0)

        # Double ARAPUCA walls - centered subtraction
        double_wall_shape = geom.shapes.Boolean("XARAPUCA_double_wall_shape",
                                type='subtraction',
                                first=out_box,
                                second=double_in_box)

        # Double acceptance window - different dimensions
        double_window_shape = geom.shapes.Box("XARAPUCA_double_window_shape",
                                            dx=self.params['ArapucaAcceptanceWindow_x']/2.0,
                                            dy=(self.params['ArapucaOut_y'] - Q('0.02cm'))/2.0,
                                            dz=self.params['ArapucaAcceptanceWindow_z']/2.0)

       
        # Create volumes
        # Regular ARAPUCA
        wall_vol = geom.structure.Volume("volXARAPUCAWall",
                                    material="G10",
                                    shape=wall_shape)

        window_vol = geom.structure.Volume("volXARAPUCAWindow", 
                                        material="LAr",
                                        shape=window_shape)
        window_vol.params.append(("SensDet","PhotonDetector"))

        # Double ARAPUCA
        double_wall_vol = geom.structure.Volume("volXARAPUCADoubleWall",
                                            material="G10", 
                                            shape=double_wall_shape)

        double_window_vol = geom.structure.Volume("volXARAPUCADoubleWindow",
                                                material="LAr",
                                                shape=double_window_shape)
        double_window_vol.params.append(("SensDet","PhotonDetector"))


       


        # Add volumes to builder
        self.add_volume(wall_vol)
        self.add_volume(window_vol)
        self.add_volume(double_wall_vol)
        self.add_volume(double_window_vol)

        self.construct_cathode_mesh(geom)
        

    def calculate_cathode_positions(self, idx, cathode_center_x, cathode_center_y, cathode_center_z):
        '''Calculate positions of X-ARAPUCAs over the cathode'''
        positions = []
        
        for i in range(4):
            # Calculate x,y,z position for each ARAPUCA
            # Use the existing position calculations from PERL
            x = cathode_center_x  
            if i == 0:
                y = -2*self.cathode['widthCathodeVoid'] - 2.0*self.cathode['CathodeBorder'] + self.params['GapPD'] + 0.5*self.params['ArapucaOut_x'] + cathode_center_y
                z = 0.5*self.cathode['lengthCathodeVoid'] + self.cathode['CathodeBorder'] + cathode_center_z
            elif i == 1:
                y = -self.cathode['CathodeBorder'] - self.params['GapPD'] - 0.5*self.params['ArapucaOut_x'] + cathode_center_y
                z = -1.5*self.cathode['lengthCathodeVoid'] - 2.0*self.cathode['CathodeBorder'] + cathode_center_z
            elif i == 2:
                y = -(-self.cathode['CathodeBorder'] - self.params['GapPD'] - 0.5*self.params['ArapucaOut_x']) + cathode_center_y
                z = -(-1.5*self.cathode['lengthCathodeVoid'] - 2.0*self.cathode['CathodeBorder']) + cathode_center_z
            else:
                y = -(-2*self.cathode['widthCathodeVoid'] - 2.0*self.cathode['CathodeBorder'] + self.params['GapPD'] + 0.5*self.params['ArapucaOut_x']) + cathode_center_y # Mirror of position 0
                z = -(0.5*self.cathode['lengthCathodeVoid'] + self.cathode['CathodeBorder']) + cathode_center_z # Mirror of position 0
                
            if (idx == 1 and i == 3):
                y = -(-self.cathode['CathodeBorder'] - self.params['GapPD'] - 0.5*self.params['ArapucaOut_x']) + cathode_center_y

            positions.append((x,y,z))
            
        return positions

    def calculate_lateral_positions(self, frame_center_x, frame_center_y, frame_center_z):
        '''Calculate positions of X-ARAPUCAs on lateral walls'''
        positions = []
        
        # Calculate positions using parameters similar to PERL script
        for i in range(8):
            x = frame_center_x
            
            if i < 4:
                y = frame_center_y
                if i == 0:
                    x += self.params['Upper_FirstFrameVertDist']
            else:
                y = frame_center_y + 2*self.cathode['widthCathode'] + 2*(self.params['CathodeFrameToFC'] + 
                    self.params['FCToArapucaSpaceLat'] - self.params['ArapucaOut_y']/2)
                if i == 4:
                    x += self.params['Upper_FirstFrameVertDist']
                    
            if i in [1,5]:
                x -= self.params['VerticalPDdist']
            elif i in [2,6]:
                x = frame_center_x - self.params['Lower_FirstFrameVertDist'] 
            elif i in [3,7]:
                x += self.params['VerticalPDdist']
                
            z = frame_center_z
            
            positions.append((x,y,z))
            
        return positions