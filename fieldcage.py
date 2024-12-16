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

    def construct_thick_profile(self, geom, fc_corner):
        """Construct the thick field cage profile through a series of Boolean operations"""
        
        # Create short field cage components
        short_halfcirc = geom.shapes.Tubs(
            "ShortFChalfcirc",
            rmin=Q('0mm'),
            rmax=Q('3.18mm'),
            dz=10*self.length/2.,
            sphi="-90deg",
            dphi="180deg"
        )

        short_rect = geom.shapes.Box(
            "ShortFCrect",
            dx=Q('10.42mm')/2,
            dy=Q('1mm')/2,
            dz=10*self.length/2
        )

        short_cutter = geom.shapes.Box(
            "ShortFCcutter",
            dx=Q('0.51mm')/2,
            dy=Q('6.37mm')/2,
            dz=10*self.cut_length/2
        )

        short_arc1 = geom.shapes.Tubs(
            "ShortFCarc1",
            rmin=Q('27.58mm'),
            rmax=Q('28.58mm'),
            dz=10*self.length/2.,
            sphi="56deg",
            dphi="25deg"
        )

        short_arc2 = geom.shapes.Tubs(
            "ShortFCarc2",
            rmin=Q('64.09mm'),
            rmax=Q('65.09mm'),
            dz=10*self.length/2.,
            sphi="81deg",
            dphi="9deg"
        )

        # Cut half circle
        short_halfcirc_cut = geom.shapes.Boolean(
            "ShortFChalfcircCut",
            type='subtraction',
            first=short_halfcirc,
            second=short_cutter,
            pos=geom.structure.Position(
                "posfc1",
                x=Q('0.249mm'),
                y=Q('0mm'),
                z=Q('0mm')
            )
        )

        # Add rectangle
        short_circ_rect = geom.shapes.Boolean(
            "ShortFCcircAndRect",
            type='union',
            first=short_halfcirc_cut,
            second=short_rect,
            pos=geom.structure.Position(
                "posfc2",
                x=Q('-4.705mm'),
                y=Q('-2.68mm'),
                z=Q('0mm')
            )
        )

        # Add first arc
        short_with_arc1 = geom.shapes.Boolean(
            "ShortFCwithArc1",
            type='union',
            first=short_circ_rect,
            second=short_arc1,
            pos=geom.structure.Position(
                "posfc3",
                x=Q('-14.204mm'),
                y=Q('-21.1mm'),
                z=Q('0mm')
            )
        )

        # Add second arc
        short_with_arc2 = geom.shapes.Boolean(
            "ShortFCwithArc2",
            type='union',
            first=short_with_arc1,
            second=short_arc2,
            pos=geom.structure.Position(
                "posfc4",
                x=Q('-19.84mm'),
                y=Q('-57.16mm'),
                z=Q('0mm')
            )
        )

        # Make the complete short profile
        short_profile = geom.shapes.Boolean(
            "ShortFCProfile",
            type='union',
            first=short_with_arc2,
            second=short_with_arc2,
            pos=geom.structure.Position(
                "posfc5",
                x=Q('-39.68mm'),
                y=Q('0mm'),
                z=Q('0mm')
            ),
            rot=geom.structure.Rotation(
                "rotfc5",
                x="0deg",
                y="180deg",
                z="0deg"
            )
        )

        # Create long field cage components
        long_halfcirc = geom.shapes.Tubs(
            "LongFChalfcirc",
            rmin=Q('0mm'),
            rmax=Q('3.18mm'),
            dz=10*self.width/2.,
            sphi="-90deg",
            dphi="180deg"
        )

        long_rect = geom.shapes.Box(
            "LongFCrect",
            dx=Q('10.42mm')/2,
            dy=Q('1mm')/2,
            dz=10*self.width/2
        )

        long_cutter = geom.shapes.Box(
            "LongFCcutter",
            dx=Q('0.51mm')/2,
            dy=Q('6.37mm')/2,
            dz=10*self.cut_width/2
        )

        long_arc1 = geom.shapes.Tubs(
            "LongFCarc1",
            rmin=Q('27.58mm'),
            rmax=Q('28.58mm'),
            dz=10*self.width/2.,
            sphi="56deg",
            dphi="25deg"
        )

        long_arc2 = geom.shapes.Tubs(
            "LongFCarc2",
            rmin=Q('64.09mm'),
            rmax=Q('65.09mm'),
            dz=10*self.width/2.,
            sphi="81deg",
            dphi="9deg"
        )

        # Cut half circle
        long_halfcirc_cut = geom.shapes.Boolean(
            "LongFChalfcircCut",
            type='subtraction',
            first=long_halfcirc,
            second=long_cutter,
            pos=geom.structure.Position(
                "posfc6",
                x=Q('0.249mm'),
                y=Q('0mm'),
                z=Q('0mm')
            )
        )

        # Add rectangle
        long_circ_rect = geom.shapes.Boolean(
            "LongFCcircAndRect",
            type='union',
            first=long_halfcirc_cut,
            second=long_rect,
            pos=geom.structure.Position(
                "posfc7",
                x=Q('-4.705mm'),
                y=Q('-2.68mm'),
                z=Q('0mm')
            )
        )

        # Add first arc
        long_with_arc1 = geom.shapes.Boolean(
            "LongFCwithArc1",
            type='union',
            first=long_circ_rect,
            second=long_arc1,
            pos=geom.structure.Position(
                "posfc8",
                x=Q('-14.204mm'),
                y=Q('-21.1mm'),
                z=Q('0mm')
            )
        )

        # Add second arc
        long_with_arc2 = geom.shapes.Boolean(
            "LongFCwithArc2",
            type='union',
            first=long_with_arc1,
            second=long_arc2,
            pos=geom.structure.Position(
                "posfc9",
                x=Q('-19.84mm'),
                y=Q('-57.16mm'),
                z=Q('0mm')
            )
        )

        # Make the complete long profile
        long_profile = geom.shapes.Boolean(
            "LongFCProfile",
            type='union',
            first=long_with_arc2,
            second=long_with_arc2,
            pos=geom.structure.Position(
                "posfc10",
                x=Q('-39.68mm'),
                y=Q('0mm'),
                z=Q('0mm')
            ),
            rot=geom.structure.Rotation(
                "rotfc10",
                x="0deg",
                y="180deg",
                z="0deg"
            )
        )

        # Now build the full field cage structure
        # Start with short profile and add corner
        fs1 = geom.shapes.Boolean(
            "FSunion1",
            type='union',
            first=short_profile,
            second=fc_corner,
            pos=geom.structure.Position(
            "cornerpos1",
            x=Q('-2cm'),
            y=-self.tor_rad,
            z=0.5*self.length
            ),
            rot="rPlus90AboutXPlus90AboutZ"
        )

        # Add long profile
        fs2 = geom.shapes.Boolean(
            "FSunion2",
            type='union',
            first=fs1,
            second=long_profile,
            pos=geom.structure.Position(
            "LongFCProfile1",
            x=Q('0cm'),
            y=-(0.5*self.width + self.tor_rad),
            z=0.5*self.length + self.tor_rad
            ),
            rot="rPlus90AboutX"
        )

        # Continue with remaining unions...
        fs3 = geom.shapes.Boolean(
            "FSunion3",
            type='union',
            first=fs2,
            second=fc_corner,
            pos=geom.structure.Position(
            "cornerpos2",
            x=Q('-2cm'),
            y=-(self.width + self.tor_rad),
            z=0.5*self.length
            ),
            rot=geom.structure.Rotation(
            "rotfs3",
            x="270deg",
            y="270deg",
            z="270deg"
            )
        )

        fs4 = geom.shapes.Boolean(
            "FSunion4",
            type='union',
            first=fs3,
            second=short_profile,
            pos=geom.structure.Position(
            "ShortFCProfile2",
            x=Q('-3.968cm'),
            y=-(self.width + 2*self.tor_rad),
            z=Q('0cm')
            ),
            rot=geom.structure.Rotation(
            "rotfs4",
            x="0deg",
            y="0deg",
            z="180deg"
            )
        )

        # Complete the field cage with final unions
        final_shape = geom.shapes.Boolean(
            "FieldShaperSolid",
            type='union',
            first=fs4,
            second=fc_corner,
            pos=geom.structure.Position(
            "cornerpos4",
            x=Q('-2cm'),
            y=-self.tor_rad,
            z=-0.5*self.length
            ),
            rot=geom.structure.Rotation(
            "rotfs7",
            x="90deg",
            y="90deg",
            z="90deg"
            )
        )

        return final_shape


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
