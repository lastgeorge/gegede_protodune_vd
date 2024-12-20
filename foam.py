#!/usr/bin/env python
'''
Foam Builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class FoamBuilder(gegede.builder.Builder):
    '''Build the foam for ProtoDUNE-VD'''

    def configure(self, 
                 FoamPadding=None,
                 cryostat_parameters=None,
                 steel_parameters=None, 
                 beam_parameters=None,
                 print_config=False,
                 print_construct=False,
                 **kwargs):
        
        if print_config:
            print('Configure Foam <- ProtoDUNE-VD <- World')
            
        self.print_construct = print_construct
        self.FoamPadding = FoamPadding
        self.cryo = cryostat_parameters
        self.steel = steel_parameters  
        self.beam = beam_parameters

    def construct(self, geom):
        if self.print_construct:
            print('Construct Foam <- ProtoDUNE-VD <- World')

        # Create the main foam block shape
        foam_block = geom.shapes.Box(
            "FoamPadBlock",
            dx=(self.cryo['Cryostat_x'] + 2*self.FoamPadding)/2,
            dy=(self.cryo['Cryostat_y'] + 2*self.FoamPadding)/2,
            dz=(self.cryo['Cryostat_z'] + 2*self.FoamPadding)/2
        )

        # Create cryostat shape to subtract
        cryo_shape = geom.shapes.Box(
            "Cryostat",
            dx=self.cryo['Cryostat_x']/2,
            dy=self.cryo['Cryostat_y']/2,
            dz=self.cryo['Cryostat_z']/2
        )

        # Create subtraction to make foam shell
        foam_nobw = geom.shapes.Boolean(
            "FoamPaddingNoBW",
            type='subtraction', 
            first=foam_block,
            second=cryo_shape
        )

        # Get beam window parameters
        bw_foam_rem = geom.shapes.CutTubs(
            "BeamWindowFoamRemp",
            rmin=Q('0cm'),
            rmax=self.beam['BeamPipeRad'],
            dz=self.beam['BeamWFoRemLe']/2,
            sphi=Q('0deg'),
            dphi=Q('360deg'),
            normalm=(-0.71030185483404029, 0, -0.70389720486682006),
            normalp=(0.71030185483404018, 0, 0.70389720486682017)
        )

        # Final foam shape with beam window hole
        foam_shape = geom.shapes.Boolean(
            "FoamPadding",
            type='subtraction',
            first=foam_nobw,
            second=bw_foam_rem,
            pos=geom.structure.Position(
                "posBWFoPa",
                x=self.beam['BeamWFoRem_x'],
                y=self.beam['BeamWFoRem_y'], 
                z=self.beam['BeamWFoRem_z']
            ),
            rot='rBeamW3'
        )

        # Create foam volume
        foam_vol = geom.structure.Volume(
            "volFoamPadding",
            material="foam_protoDUNE_RPUF_assayedSample", 
            shape=foam_shape
        )

        self.add_volume(foam_vol)

    def place_in_volume(self, geom, main_lv):
        """Place foam padding in the main volume"""
        foam_vol = self.get_volume('volFoamPadding')
        
        foam_pos = geom.structure.Position(
            "posFoamPadding",
            x=self.steel['posCryoInDetEnc']['x'],
            y=self.steel['posCryoInDetEnc']['y'],
            z=self.steel['posCryoInDetEnc']['z']
        )
        
        foam_place = geom.structure.Placement(
            "placeFoamPadding",
            volume=foam_vol,
            pos=foam_pos
        )
        
        main_lv.placements.append(foam_place.name)

