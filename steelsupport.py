#!/usr/bin/env python
'''
Steel Builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class SteelSupportBuilder(gegede.builder.Builder):
    '''Build the steel support structure for ProtoDUNE-VD'''

    def configure(self,
                 steel_parameters=None,
                 print_config=False,  
                 print_construct=False,  # Add this line
                 **kwargs):
        
        if print_config:
            print('Configure Steel Support  <- ProtoDUNE-VD <- World')
        
        self.print_construct = print_construct

        if steel_parameters:
            self.params = {
                'SteelSupport_x': steel_parameters.get('SteelSupport_x'),
                'SteelSupport_y': steel_parameters.get('SteelSupport_y'),
                'SteelSupport_z': steel_parameters.get('SteelSupport_z'),
                'SteelPlate': steel_parameters.get('SteelPlate'),
                'FracMassOfSteel': steel_parameters.get('FracMassOfSteel'),
                'FracMassOfAir': steel_parameters.get('FracMassOfAir'),
                'SpaceSteelSupportToWall': steel_parameters.get('SpaceSteelSupportToWall'),
                'SpaceSteelSupportToCeiling': steel_parameters.get('SpaceSteelSupportToCeiling')
            }
        
    # ...existing code...

    def construct_TB(self, geom):
        """Construct the top/bottom steel support structure"""
        
        # Create main TB volume 
        tb_shape = geom.shapes.Box("boxCryoTop",
                                dx=Q("1016.8cm")/2, 
                                dy=Q("1016.8cm")/2,
                                dz=Q("61.8cm")/2)
        
        tb_vol = geom.structure.Volume("volSteelSupport_TB",
                                    material="Air",
                                    shape=tb_shape)

        # Place the center unit volumes (5x5 grid)
        for i in range(5):  # x positions: -320, -160, 0, 160, 320
            for j in range(5):  # y positions: -320, -160, 0, 160, 320
                x = Q(f"{-320 + i*160}cm")
                y = Q(f"{-320 + j*160}cm") 
                z = Q("0cm")
                
                # Get central unit volume from earlier construction
                cent_vol = self.get_volume("volUnitCent")
                
                pos = geom.structure.Position(
                    f"posUnitTBCent_{i}-{j}",
                    x=x, y=y, z=z)
                    
                place = geom.structure.Placement(
                    f"volUnitTBCent_{i}-{j}",
                    volume=cent_vol,
                    pos=pos)
                    
                tb_vol.placements.append(place.name)

        # Place the edge unit volumes 
        edge_positions = {
            'E': {'x': Q("454.2cm"), 'rot': None},
            'S': {'x': Q("0cm"), 'rot': "rotTBS"},  
            'W': {'x': Q("-454.2cm"), 'rot': "rotTBW"},
            'N': {'x': Q("0cm"), 'rot': "rotTBN"}
        }
        
        for i in range(5):  # For each row/column
            y = Q(f"{-320 + i*160}cm")
            
            # Get edge unit volume
            top_vol = self.get_volume("volUnitTop")
            
            for edge, params in edge_positions.items():
                pos = geom.structure.Position(
                    f"posUnitTB{edge}_{i}",
                    x=params['x'],
                    y=y,
                    z=Q("0cm"))
                    
                if params['rot']:
                    # Create rotation for this edge
                    if edge == 'S':
                        rot = geom.structure.Rotation(
                            f"{params['rot']}_{i}", x="0deg", y="0deg", z="-90deg")
                    elif edge == 'W':
                        rot = geom.structure.Rotation(
                            f"{params['rot']}_{i}", x="0deg", y="0deg", z="-180deg")  
                    elif edge == 'N':
                        rot = geom.structure.Rotation(
                            f"{params['rot']}_{i}", x="0deg", y="0deg", z="-270deg")
                        
                    place = geom.structure.Placement(
                        f"volUnitTB{edge}_{i}",
                        volume=top_vol,
                        pos=pos,
                        rot=rot)
                else:
                    place = geom.structure.Placement(
                        f"volUnitTB{edge}_{i}",
                        volume=top_vol, 
                        pos=pos)
                    
                tb_vol.placements.append(place.name)

        self.add_volume(tb_vol)
        return tb_vol

    def construct_unit_volumes(self, geom):
        """Construct the central and top unit volumes for the steel support structure"""
        
        # Define parameters for central and top units
        unit_params = {
            'central': {
                'box1': {'dx': Q('160cm'), 'dy': Q('160cm'), 'dz': Q('61.8cm')},
                'box2': {'dx': Q('158.2cm'), 'dy': Q('158.2cm'), 'dz': Q('56.2cm')},
                'box3': {'dx': Q('137.2cm'), 'dy': Q('137.2cm'), 'dz': Q('61.801cm')},
                'box4': {'dx': Q('158.2cm'), 'dy': Q('13.6cm'), 'dz': Q('27.4cm')},
                'box5': {'dx': Q('158.2cm'), 'dy': Q('6.425cm'), 'dz': Q('24.96cm')},
                'bar_positions': {
                    'x': Q('0cm'),
                    'y': [Q('3.5876cm'), Q('-3.5876cm')],
                    'z': Q('-17.2cm')
                }
            },
            'top': {
                'box1': {'dx': Q('108.4cm'), 'dy': Q('160cm'), 'dz': Q('61.8cm')},
                'box2': {'dx': Q('107.5cm'), 'dy': Q('158.2cm'), 'dz': Q('56.2cm')},
                'box3': {'dx': Q('97cm'), 'dy': Q('137.2cm'), 'dz': Q('61.81cm')},
                'box4': {'dx': Q('107.5cm'), 'dy': Q('13.6cm'), 'dz': Q('27.4cm')},
                'box5': {'dx': Q('107.5cm'), 'dy': Q('6.425cm'), 'dz': Q('24.96cm')},
                'bar_positions': {
                    'x': [Q('5.6cm'), Q('0.45cm')],
                    'y': [Q('3.5876cm'), Q('-3.5876cm')],
                    'z': Q('-17.2cm')
                }
            }
        }

        def create_boxes(params, prefix):
            """Helper to create basic box shapes"""
            boxes = {}
            for i in range(1, 6):
                box_params = params[f'box{i}']
                boxes[f'box{i}'] = geom.shapes.Box(
                    f"{prefix}box{i}",
                    dx=box_params['dx']/2,
                    dy=box_params['dy']/2,
                    dz=box_params['dz']/2
                )
            return boxes

        def construct_unit(unit_type, boxes):
            """Helper to construct a unit (central or top) through boolean operations"""
            prefix = 'Top' if unit_type == 'top' else ''
            params = unit_params[unit_type]
            
            # Create hollow box
            box_hollow = geom.shapes.Boolean(
                f"box{prefix}Holl",
                type='subtraction',
                first=boxes['box1'],
                second=boxes['box2'],
                pos=geom.structure.Position(
                    f"posbox{prefix}Holl",
                    x=Q('0.451cm') if unit_type == 'top' else Q('0cm'),
                    y=Q('0cm'),
                    z=Q('0cm')
                )
            )

            # Remove central hole
            box_large = geom.shapes.Boolean(
                f"boxLarge{prefix}",
                type='subtraction',
                first=box_hollow,
                second=boxes['box3'],
                pos=geom.structure.Position(
                    f"posboxLarge{prefix}",
                    x=Q('5.701cm') if unit_type == 'top' else Q('0cm'),
                    y=Q('0cm'),
                    z=Q('0cm')
                )
            )

            # Create cross bars
            bar = boxes['box4']
            for i, y_pos in enumerate(params['bar_positions']['y']):
                bar = geom.shapes.Boolean(
                    f"boxBar{prefix}{i}",
                    type='subtraction',
                    first=bar,
                    second=boxes['box5'],
                    pos=geom.structure.Position(
                        f"posboxBar{prefix}{i}",
                        x=Q('0cm'),
                        y=y_pos,
                        z=Q('0cm')
                    )
                )

            # Combine pieces
            final_shape = box_large
            for i, x_pos in enumerate(params['bar_positions']['x'] if unit_type == 'top' else [params['bar_positions']['x']]):
                rot = geom.structure.Rotation(
                    f"rot{prefix}{i}",
                    x="0deg",
                    y="0deg",
                    z="90deg" if i == 0 else "0deg"
                )
                final_shape = geom.shapes.Boolean(
                    f"Unit{prefix}{i}",
                    type='union',
                    first=final_shape,
                    second=bar,
                    pos=geom.structure.Position(
                        f"pos{prefix}{i}",
                        x=x_pos,
                        y=Q('0cm'),
                        z=params['bar_positions']['z']
                    ),
                    rot=None if unit_type == 'top' else rot
                )

            return final_shape

        # Create volumes for both unit types
        for unit_type in ['central', 'top']:
            boxes = create_boxes(unit_params[unit_type], unit_type[0])
            shape = construct_unit(unit_type, boxes)
            
            vol = geom.structure.Volume(
                f"volUnit{'Top' if unit_type == 'top' else 'Cent'}",
                material="STEEL_STAINLESS_Fe7Cr2Ni",
                shape=shape
            )
            self.add_volume(vol)

    def construct(self, geom):
        if self.print_construct:
            print('Construct Steel Support <- ProtoDUNE-VD <- World')

        # First construct the component volumes
        self.construct_unit_volumes(geom)
            
        # Construct top/bottom steel support structure
        tb_vol = self.construct_TB(geom)
        
        # Create position for top steel support
        top_pos = geom.structure.Position(
            "posSteelSupport_Top",
            x=Q("0cm"),
            y=self.params['posTopSteelStruct'] + Q("61.1cm"),
            z=Q("0cm"))
            
        top_rot = geom.structure.Rotation(
            "rotSteelSupport_Top",
            x="90deg", y="0deg", z="0deg")
            
        # Create placement
        top_place = geom.structure.Placement(
            "placeSteelSupport_Top",
            volume=tb_vol,
            pos=top_pos,
            rot=top_rot)
            
        # Add to main support volume
        support_vol = self.get_volume("volSteelSupport")
        support_vol.placements.append(top_place.name)
