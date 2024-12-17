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
            self.params = steel_parameters.copy()
        
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

        # Place the edge unit volumes (E, S, W, N) for each row
        for i in range(5):  # x positions: -320 to 320 in steps of 160
            x_base = Q(f"{-320 + i*160}cm")
            y_base = Q(f"{-320}cm")  

            # Get edge unit volume
            top_vol = self.get_volume("volUnitTop")

            # East edge (TBE)
            pos_e = geom.structure.Position(
                f"posUnitTBE_{i}",
                x=Q("454.2cm"),
                y=y_base + i*Q("160cm"),
                z=Q("0cm"))
            
            place_e = geom.structure.Placement(
                f"volUnitTBE_{i}",
                volume=top_vol,
                pos=pos_e)
            tb_vol.placements.append(place_e.name)

            # South edge (TBS)
            pos_s = geom.structure.Position(
                f"posUnitTBS_{i}",
                x=x_base,
                y=Q("454.2cm"),
                z=Q("0cm"))
            
            rot_s = geom.structure.Rotation(
                f"rotUnitTBS_{i}", 
                x="0deg", y="0deg", z="-90deg")

            place_s = geom.structure.Placement(
                f"volUnitTBS_{i}",
                volume=top_vol,
                pos=pos_s,
                rot=rot_s)
            tb_vol.placements.append(place_s.name)

            # West edge (TBW)
            pos_w = geom.structure.Position(
                f"posUnitTBW_{i}",
                x=Q("-454.2cm"),
                y=y_base + i*Q("160cm"),
                z=Q("0cm"))
            
            rot_w = geom.structure.Rotation(
                f"rotUnitTBW_{i}",
                x="0deg", y="0deg", z="-180deg")

            place_w = geom.structure.Placement(
                f"volUnitTBW_{i}",
                volume=top_vol,
                pos=pos_w,
                rot=rot_w)
            tb_vol.placements.append(place_w.name)

            # North edge (TBN)
            pos_n = geom.structure.Position(
                f"posUnitTBN_{i}",
                x=x_base,
                y=Q("-454.2cm"),
                z=Q("0cm"))
            
            rot_n = geom.structure.Rotation(
                f"rotUnitTBN_{i}",
                x="0deg", y="0deg", z="-270deg")

            place_n = geom.structure.Placement(
                f"volUnitTBN_{i}",
                volume=top_vol,
                pos=pos_n,
                rot=rot_n)
            tb_vol.placements.append(place_n.name)


        self.add_volume(tb_vol)
        return tb_vol

    def construct_unit_volumes(self, geom):
        """Construct the central and top unit volumes that make up the steel support structure"""
        
        # Define parameters for central and top units
        unit_params = {
            'central': {
                'main_box': {'dx': Q('160cm'), 'dy': Q('160cm'), 'dz': Q('61.8cm')},
                'inner_box': {'dx': Q('158.2cm'), 'dy': Q('158.2cm'), 'dz': Q('56.2cm')},
                'hole': {'dx': Q('137.2cm'), 'dy': Q('137.2cm'), 'dz': Q('61.801cm')},
                'cross_bar': {'dx': Q('158.2cm'), 'dy': Q('13.6cm'), 'dz': Q('27.4cm')},
                'bar_hole': {'dx': Q('158.2cm'), 'dy': Q('6.425cm'), 'dz': Q('24.96cm')},
                'offsets': {'x': Q('0cm'), 'y': Q('0cm')},
                'name': 'Cent'
            },
            'top': {
                'main_box': {'dx': Q('108.4cm'), 'dy': Q('160cm'), 'dz': Q('61.8cm')},
                'inner_box': {'dx': Q('107.5cm'), 'dy': Q('158.2cm'), 'dz': Q('56.2cm')},
                'hole': {'dx': Q('97cm'), 'dy': Q('137.2cm'), 'dz': Q('61.81cm')},
                'cross_bar': {'dx': Q('107.5cm'), 'dy': Q('13.6cm'), 'dz': Q('27.4cm')},
                'bar_hole': {'dx': Q('107.5cm'), 'dy': Q('6.425cm'), 'dz': Q('24.96cm')},
                'offsets': {'x': Q('5.701cm'), 'y': Q('0.451cm')},
                'name': 'Top'
            }
        }

        def create_box(name, dx, dy, dz):
            """Helper to create box shape"""
            return geom.shapes.Box(name, dx=dx/2, dy=dy/2, dz=dz/2)

        def create_bar_with_holes(params, prefix):
            """Helper to create cross bar with holes"""
            bar = create_box(f"box{prefix}Bar", **params['cross_bar'])
            hole = create_box(f"box{prefix}Hole", **params['bar_hole'])

            # Create holes in bar
            bar_i = geom.shapes.Boolean(f"boxBar{prefix}I",
                type='subtraction',
                first=bar,
                second=hole,
                pos=geom.structure.Position(f"posBoxBar{prefix}I",
                    x=Q('0cm'), y=Q('3.5876cm'), z=Q('0cm')))

            return geom.shapes.Boolean(f"boxBar{prefix}",
                type='subtraction',
                first=bar_i,
                second=hole,
                pos=geom.structure.Position(f"posBoxBar{prefix}",
                    x=Q('0cm'), y=Q('-3.5876cm'), z=Q('0cm')))

        # Create bars with respective parameters
        bar_cent = create_bar_with_holes(unit_params['central'], 'central')
        bar_top = create_bar_with_holes(unit_params['top'], 'top')

        # Create unit volumes
        for unit_type, params in unit_params.items():
            # Create main shapes
            box1 = create_box(f"box1_{unit_type}", **params['main_box'])
            box2 = create_box(f"box2_{unit_type}", **params['inner_box'])
            box3 = create_box(f"box3_{unit_type}", **params['hole'])

            # Hollow out main box
            box_hollow = geom.shapes.Boolean(f"boxHoll_{unit_type}",
                type='subtraction',
                first=box1,
                second=box2,
                pos=geom.structure.Position(f"posboxHoll_{unit_type}",
                    x=params['offsets']['y'], y=Q('0cm'), z=Q('0cm')))

            # Remove central hole
            box_large = geom.shapes.Boolean(f"boxLarge_{unit_type}",
                type='subtraction',
                first=box_hollow,
                second=box3,
                pos=geom.structure.Position(f"posboxLarge_{unit_type}",
                    x=params['offsets']['x'], y=Q('0cm'), z=Q('0cm')))


            # Add first cross bar (different for central vs top)
            if unit_type == 'central':
                box_uni = geom.shapes.Boolean("boxUniCent",
                    type='union',
                    first=box_large,
                    second=bar_cent,
                    pos=geom.structure.Position("posBoxUniCent",
                        x=Q('0cm'), y=Q('0cm'), z=Q('-17.2cm')))
            else:
                # For top unit, first union uses bar_cent rotated 90
                box_uni = geom.shapes.Boolean("boxUniTop",
                    type='union',
                    first=box_large,
                    second=bar_cent,
                    pos=geom.structure.Position("posboxUni1",
                        x=Q('5.6cm'), y=Q('0cm'), z=Q('-17.2cm')),
                    rot=geom.structure.Rotation("rotUni1",
                        x="0deg", y="0deg", z="90deg"))

            # Add second bar
            if unit_type == 'central':
                # Central unit: add rotated bar_cent
                final_shape = geom.shapes.Boolean("UnitCent",
                    type='union',
                    first=box_uni,
                    second=bar_cent,
                    pos=geom.structure.Position("posUnitCent",
                        x=Q('0cm'), y=Q('0cm'), z=Q('-17.2cm')),
                    rot=geom.structure.Rotation("rotUnitCent",
                        x="0deg", y="0deg", z="90deg"))
            else:
                # Top unit: add bar_top without rotation
                final_shape = geom.shapes.Boolean("UnitTop", 
                    type='union',
                    first=box_uni,
                    second=bar_top,
                    pos=geom.structure.Position("posUniTop",
                        x=Q('0.45cm'), y=Q('0cm'), z=Q('-17.2cm')))
    

            # Create volume
            vol = geom.structure.Volume(f"volUnit{params['name']}",
                material="STEEL_STAINLESS_Fe7Cr2Ni",
                shape=final_shape)

            self.add_volume(vol)

    def construct(self, geom):
        if self.print_construct:
            print('Construct Steel Support <- ProtoDUNE-VD <- World')

        # First construct the component volumes
        self.construct_unit_volumes(geom)
            
        # Construct top/bottom steel support structure
        self.construct_TB(geom)
        

    def place_in_volume(self, geom, main_lv):
        """Place steel support structure in the given volume"""
        
        # Get steel support volume
        steel_TB_vol = self.get_volume('volSteelSupport_TB')
        
        # Configuration for top and bottom placements
        placements = [
            {
                'name': 'Top',
                'y_offset': Q("61.1cm"),
                'pos_param': 'posTopSteelStruct',
                'rotation': "90deg"
            },
            {
                'name': 'Bottom',
                'y_offset': -Q("61.1cm"),
                'pos_param': 'posBotSteelStruct',
                'rotation': "-90deg"
            }
        ]
        
        # Create placements for both top and bottom
        for cfg in placements:
            pos = geom.structure.Position(
                f"posSteelSupport_{cfg['name']}",
                x=Q("0cm"),
                y=self.params[cfg['pos_param']] + cfg['y_offset'],
                z=Q("0cm"))
            
            rot = geom.structure.Rotation(
                f"rotSteelSupport_{cfg['name']}",
                x=cfg['rotation'], y="0deg", z="0deg")
            
            place = geom.structure.Placement(
                f"placeSteelSupport_{cfg['name']}",
                volume=steel_TB_vol,
                pos=pos,
                rot=rot)
            
            main_lv.placements.append(place.name)



