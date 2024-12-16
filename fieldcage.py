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
                 fieldcage_parameters=None,
                 print_config=False,
                 print_construct=False,
                 **kwds):
        
        if print_config:
            print('Configure Field Cage <- Cryostat <- ProtoDUNE-VD <- World')
        # Add guard against double configuration
        if hasattr(self, '_configured'):
            return
        
        if fieldcage_parameters:
            self.inner_radius = fieldcage_parameters.get('FieldShaperInnerRadius')
            self.outer_radius = fieldcage_parameters.get('FieldShaperOuterRadius')
            self.slim_inner_radius = fieldcage_parameters.get('FieldShaperSlimInnerRadius')
            self.slim_outer_radius = fieldcage_parameters.get('FieldShaperSlimOuterRadius')
            self.tor_rad = fieldcage_parameters.get('FieldShaperTorRad')
            self.separation = fieldcage_parameters.get('FieldShaperSeparation') 
            self.n_shapers = fieldcage_parameters.get('NFieldShapers')
            self.base_length = fieldcage_parameters.get('FieldShaperBaseLength')
            self.base_width = fieldcage_parameters.get('FieldShaperBaseWidth')

            # Calculate derived dimensions
            self.length = self.base_length - 2*self.tor_rad
            self.width = self.base_width - 2*self.tor_rad
            
            self.cut_length = self.length + Q('0.02cm')
            self.cut_width = self.width + Q('0.02cm')

            self.cage_size_x = self.separation * self.n_shapers + Q('2cm')
            self.cage_size_y = self.width + Q('2cm') 
            self.cage_size_z = self.length + Q('2cm')

        self.print_construct = print_construct

        # Mark as configured
        self._configured = True

    def create_profile_components(self, geom, is_long=False):
        """Helper method to create basic field cage components"""
        length = self.width if is_long else self.length
        cut_length = self.cut_width if is_long else self.cut_length
        prefix = "Long" if is_long else "Short"
        
        components = {}
        
        # Basic shapes parameters
        shapes_params = {
            'halfcirc': {
                'rmin': Q('0mm'),
                'rmax': Q('3.18mm'),
                'dz': 10*length/2.,
                'sphi': "-90deg",
                'dphi': "180deg"
            },
            'rect': {
                'dx': Q('10.42mm')/2,
                'dy': Q('1mm')/2,
                'dz': 10*length/2
            },
            'cutter': {
                'dx': Q('0.51mm')/2,
                'dy': Q('6.37mm')/2,
                'dz': 10*cut_length/2
            },
            'arc1': {
                'rmin': Q('27.58mm'),
                'rmax': Q('28.58mm'),
                'dz': 10*length/2.,
                'sphi': "56deg",
                'dphi': "25deg"
            },
            'arc2': {
                'rmin': Q('64.09mm'),
                'rmax': Q('65.09mm'),
                'dz': 10*length/2.,
                'sphi': "81deg",
                'dphi': "9deg"
            }
        }
        
        # Create basic shapes
        components['halfcirc'] = geom.shapes.Tubs(f"{prefix}FChalfcirc", **shapes_params['halfcirc'])
        components['rect'] = geom.shapes.Box(f"{prefix}FCrect", **shapes_params['rect'])
        components['cutter'] = geom.shapes.Box(f"{prefix}FCcutter", **shapes_params['cutter'])
        components['arc1'] = geom.shapes.Tubs(f"{prefix}FCarc1", **shapes_params['arc1'])
        components['arc2'] = geom.shapes.Tubs(f"{prefix}FCarc2", **shapes_params['arc2'])
        
        return components

    def create_profile(self, geom, components, prefix):
        """Helper method to create a field cage profile through Boolean operations"""
        # Boolean operations parameters
        bool_ops = [
            {
                'name': f"{prefix}FChalfcircCut",
                'type': 'subtraction',
                'first': components['halfcirc'],
                'second': components['cutter'],
                'pos': {'x': Q('0.249mm'), 'y': Q('0mm'), 'z': Q('0mm')}
            },
            {
                'name': f"{prefix}FCcircAndRect",
                'type': 'union',
                'second': components['rect'],
                'pos': {'x': Q('-4.705mm'), 'y': Q('-2.68mm'), 'z': Q('0mm')}
            },
            {
                'name': f"{prefix}FCwithArc1",
                'type': 'union',
                'second': components['arc1'],
                'pos': {'x': Q('-14.204mm'), 'y': Q('-21.1mm'), 'z': Q('0mm')}
            },
            {
                'name': f"{prefix}FCwithArc2",
                'type': 'union',
                'second': components['arc2'],
                'pos': {'x': Q('-19.84mm'), 'y': Q('-57.16mm'), 'z': Q('0mm')}
            }
        ]
        
        result = None
        for i, op in enumerate(bool_ops):
            pos = geom.structure.Position(f"pos{prefix}{i+1}", **op['pos'])
            if i == 0:
                result = geom.shapes.Boolean(op['name'], type=op['type'],
                                          first=op['first'], second=op['second'], pos=pos)
            else:
                result = geom.shapes.Boolean(op['name'], type=op['type'],
                                          first=result, second=op['second'], pos=pos)
        
        # Create final mirrored profile
        final_profile = geom.shapes.Boolean(
            f"{prefix}FCProfile",
            type='union',
            first=result,
            second=result,
            pos=geom.structure.Position(f"pos{prefix}final", x=Q('-39.68mm'), y=Q('0mm'), z=Q('0mm')),
            rot=geom.structure.Rotation(f"rot{prefix}final", x="0deg", y="180deg", z="0deg")
        )
        
        return final_profile

    def construct_thick_profile(self, geom, fc_corner):
        """Construct the thick field cage profile"""
        # Create short and long components
        short_components = self.create_profile_components(geom, is_long=False)
        long_components = self.create_profile_components(geom, is_long=True)
        
        # Create short and long profiles
        short_profile = self.create_profile(geom, short_components, "Short")
        long_profile = self.create_profile(geom, long_components, "Long")
        
        # Define complete field cage assembly parameters
        fc_assembly_params = [
            {
                'name': "FSunion1",
                'second': fc_corner,
                'pos': {'x': Q('-2cm'), 'y': -self.tor_rad, 'z': 0.5*self.length},
                'rot': "rPlus90AboutXPlus90AboutZ"
            },
            {
                'name': "FSunion2",
                'second': long_profile,
                'pos': {'x': Q('0cm'), 'y': -(0.5*self.width + self.tor_rad), 
                       'z': 0.5*self.length + self.tor_rad},
                'rot': "rPlus90AboutX"
            },
            {
                'name': "FSunion3",
                'second': fc_corner,
                'pos': {'x': Q('-2cm'), 'y': -(self.width + self.tor_rad), 
                       'z': 0.5*self.length},
                'rot': geom.structure.Rotation("rotfs3", x="270deg", y="270deg", z="270deg")
            },
            {
                'name': "FSunion4",
                'second': short_profile,
                'pos': {'x': Q('-3.968cm'), 'y': -(self.width + 2*self.tor_rad), 
                       'z': Q('0cm')},
                'rot': geom.structure.Rotation("rotfs4", x="0deg", y="0deg", z="180deg")
            },
            {
                'name': "FieldShaperSolid",
                'second': fc_corner,
                'pos': {'x': Q('-2cm'), 'y': -self.tor_rad, 'z': -0.5*self.length},
                'rot': geom.structure.Rotation("rotfs7", x="90deg", y="90deg", z="90deg")
            }
        ]
        
        # Build field cage assembly
        result = short_profile
        for i, params in enumerate(fc_assembly_params):
            pos = geom.structure.Position(f"cornerpos{i+1}", **params['pos'])
            result = geom.shapes.Boolean(
                params['name'],
                type='union',
                first=result,
                second=params['second'],
                pos=pos,
                rot=params['rot']
            )
        
        return result

    def construct(self, geom):
        """Construct the Field Cage geometry"""
        if self.print_construct:
            print('Construct Field Cage <- Cryostat <- ProtoDUNE-VD <- World')

        # Create corner torus shapes for thick and slim field shapers
        fc_corner = geom.shapes.Torus(
            "FieldShaperCorner",
            rmin=self.inner_radius,
            rmax=self.outer_radius,
            rtor=self.tor_rad,
            startphi="0deg",
            deltaphi="90deg"
        )

        fc_slim_corner = geom.shapes.Torus(
            "FieldShaperSlimCorner", 
            rmin=self.slim_inner_radius,
            rmax=self.slim_outer_radius,
            rtor=self.tor_rad,
            startphi="0deg",
            deltaphi="90deg"
        )

        # Create the full field cage assembly using Boolean operations
        # First build the thick field cage profile
        fc_shape = self.construct_thick_profile(geom, fc_corner)
        
        # # Then build the slim field cage profile 
        # fc_slim_shape = self.construct_slim_profile(geom)

        # # Create volumes
        # fc_vol = geom.structure.Volume(
        #     "volFieldShaper",
        #     material="ALUMINUM_Al",
        #     shape=fc_shape
        # )

        # fc_slim_vol = geom.structure.Volume(
        #     "volFieldShaperSlim",
        #     material="ALUMINUM_Al", 
        #     shape=fc_slim_shape
        # )

        # self.add_volume(fc_vol)
        # self.add_volume(fc_slim_vol)
