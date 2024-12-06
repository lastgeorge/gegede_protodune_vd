#!/usr/bin/env python
'''
Main builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

# Import the CryostatBuilder
from cryostat import CryostatBuilder

class ProtoDUNEVDBuilder(gegede.builder.Builder):
    '''
    Build the ProtoDUNE-VD detector enclosure and components
    '''
    
    def configure(self, 
                 DetEncX=None, DetEncY=None, DetEncZ=None,
                 Cryostat_x=None, Cryostat_y=None, Cryostat_z=None,
                 driftTPCActive=None, widthTPCActive=None, lengthTPCActive=None,
                 Cathode_switch=True, ArapucaMesh_switch=True,
                 HD_CRT_switch=False, DP_CRT_switch=False,
                 wirePitchU=None, wirePitchV=None, wirePitchZ=None,
                 wireAngleU=None, wireAngleV=None,
                 heightCathode=None, CathodeBorder=None,
                 widthCathodeVoid=None, lengthCathodeVoid=None,
                 ArapucaOut_x=None, ArapucaOut_y=None, ArapucaOut_z=None,
                 ArapucaIn_x=None, ArapucaIn_y=None, ArapucaIn_z=None,
                 FracMassOfSteel=0.5, FracMassOfAir=0.5,
                 SteelDensity=None, AirDensity=None,
                 **kwds):
        
        # Store all configuration parameters
        self.det_enc = (DetEncX, DetEncY, DetEncZ)
        self.cryo_dim = (Cryostat_x, Cryostat_y, Cryostat_z)
        self.active_dim = (driftTPCActive, widthTPCActive, lengthTPCActive)
        
        # Feature switches
        self.cathode_on = Cathode_switch
        self.arapuca_mesh_on = ArapucaMesh_switch
        self.hd_crt_on = HD_CRT_switch
        self.dp_crt_on = DP_CRT_switch
        
        # Wire parameters
        self.wire_pitch = (wirePitchU, wirePitchV, wirePitchZ)
        self.wire_angle = (wireAngleU, wireAngleV)
        
        # Cathode parameters
        self.cathode_params = dict(
            height = heightCathode,
            border = CathodeBorder,
            width_void = widthCathodeVoid,
            length_void = lengthCathodeVoid
        )
        
        # X-ARAPUCA parameters  
        self.arapuca_out = (ArapucaOut_x, ArapucaOut_y, ArapucaOut_z)
        self.arapuca_in = (ArapucaIn_x, ArapucaIn_y, ArapucaIn_z)
        
        # Material properties
        self.frac_steel = FracMassOfSteel
        self.frac_air = FracMassOfAir
        self.steel_density = SteelDensity
        self.air_density = AirDensity

    # define materials ...
    def construct_materials(self, geom):
        """Define all materials used in the geometry"""
        
        # Calculate mixture density
        mixture_density = (self.frac_air * self.air_density+ 
                        self.frac_steel * self.steel_density)
        
        # Define AirSteelMixture
        air_steel_mix = geom.matter.Mixture(
            "AirSteelMixture",
            density = mixture_density,
            components = (
                ("STEEL_STAINLESS_Fe7Cr2Ni", self.frac_steel),
                ("Air", self.frac_air)
            )
        )

        # Define basic elements
        fe = geom.matter.Element(
            "Iron", "Fe", 26, "55.845g/mole")
        
        ni = geom.matter.Element(
            "Nickel", "Ni", 28, "58.6934g/mole")

        # Define materials
        steel = geom.matter.Mixture(
            "STEEL_STAINLESS_Fe7Cr2Ni",
            density = "7.9300g/cc",
            components = (
                ("Iron", 0.70),
                ("Nickel", 0.30)
            ))
        
        lar = geom.matter.Molecule(
            "LAr",
            density = "1.4g/cc",
            elements = (("Ar", 1),))



    def construct(self, geom):

        # Define materials first
        self.construct_materials(geom)

        # Create detector enclosure shape
        shape = geom.shapes.Box(self.name + '_shape',
                              dx=self.det_enc[0]/2.0,
                              dy=self.det_enc[1]/2.0,
                              dz=self.det_enc[2]/2.0)
        
        # Create volume with Air material
        det_enc_vol = geom.structure.Volume(self.name + '_volume',
                                          material='Air',
                                          shape=shape)
    

        # Here we would add the construction of:
        # Cryostat
        # Get the cryostat volume from the cryostat builder
        cryo_builder = self.get_builder("cryostat")
        cryo_vol = cryo_builder.get_volume()

        # Create a placement for the cryostat in the detector enclosure
        # Place it at the center (0,0,0) since the PERL script shows posCryoInDetEnc=(0,0,0)
        cryo_pos = geom.structure.Position(
            "cryo_pos",
            x=Q('0cm'), 
            y=Q('0cm'),
            z=Q('0cm'))
        
        cryo_place = geom.structure.Placement(
            "cryo_place",
            volume=cryo_vol,
            pos=cryo_pos)

        # Add the cryostat placement to the detector enclosure volume
        det_enc_vol.placements.append(cryo_place.name)

        self.add_volume(det_enc_vol)
        # For now just create the basic structure
        # Detailed implementation of each component would follow
        
        return
