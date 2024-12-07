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
                 HD_CRT_switch=False, DP_CRT_switch=False,
                 wirePitchU=None, wirePitchV=None, wirePitchZ=None,
                 wireAngleU=None, wireAngleV=None,
                 FracMassOfSteel=0.5, FracMassOfAir=0.5,
                 SteelDensity=None, AirDensity=None,
                 **kwds):
        
        # Store all configuration parameters
        self.det_enc = (DetEncX, DetEncY, DetEncZ)
        self.cryo_dim = (Cryostat_x, Cryostat_y, Cryostat_z)
        self.active_dim = (driftTPCActive, widthTPCActive, lengthTPCActive)
        
        # Feature switches
        self.hd_crt_on = HD_CRT_switch
        self.dp_crt_on = DP_CRT_switch
        
        # Wire parameters
        self.wire_pitch = (wirePitchU, wirePitchV, wirePitchZ)
        self.wire_angle = (wireAngleU, wireAngleV)
        
        
        # Material properties
        self.frac_steel = FracMassOfSteel
        self.frac_air = FracMassOfAir
        self.steel_density = SteelDensity
        self.air_density = AirDensity

    # define materials ...
    def construct_materials(self, geom):
        """Define all materials used in the geometry"""
    
        # Define elements first
        ni = geom.matter.Element("Nickel", "Ni", 28, "58.6934g/mole")
        cr = geom.matter.Element("Chromium", "Cr", 24, "51.9961g/mole")
        fe = geom.matter.Element("Iron", "Fe", 26, "55.845g/mole")
        al = geom.matter.Element("Aluminum", "Al", 13, "26.9815g/mole")
        n = geom.matter.Element("Nitrogen", "N", 7, "14.0067g/mole")
        o = geom.matter.Element("Oxygen", "O", 8, "15.999g/mole")
        ar = geom.matter.Element("Argon", "Ar", 18, "39.948g/mole")
        c = geom.matter.Element("Carbon", "C", 6, "12.0107g/mole")
        h = geom.matter.Element("Hydrogen", "H", 1, "1.00794g/mole")
        
        # Define air
        air = geom.matter.Mixture("Air", density = "0.001225g/cc",
                                components = (("Nitrogen", 0.781),
                                            ("Oxygen", 0.209),
                                            ("Argon", 0.010)))

        # Define stainless steel
        steel = geom.matter.Mixture("STEEL_STAINLESS_Fe7Cr2Ni", 
                                density = "7.9300g/cc",
                                components = (("Iron", 0.70),
                                            ("Chromium", 0.20),
                                            ("Nickel", 0.10)))

        # Define air-steel mixture for support structure
        mixture_density = Q("0.001225g/cc") * self.frac_air + \
                        Q("7.9300g/cc") * self.frac_steel
                        
        air_steel_mix = geom.matter.Mixture("AirSteelMixture",
                                        density = mixture_density,
                                        components = (
                                            ("STEEL_STAINLESS_Fe7Cr2Ni", self.frac_steel),
                                            ("Air", self.frac_air)))


        # Define liquid argon
        lar = geom.matter.Molecule("LAr", density = "1.390g/cc",
                                elements = (("Argon", 1),))

        # Define gaseous argon
        gar = geom.matter.Molecule("GAr", density = "0.001784g/cc",
                                elements = (("Argon", 1),))

        # Define G10/FR4
        # Formula from http://pdg.lbl.gov/2014/AtomicNuclearProperties/
        g10 = geom.matter.Mixture("G10", density = "1.7g/cc",
                                components = (
                                    ("Silicon", 0.291),
                                    ("Carbon", 0.278),
                                    ("Oxygen", 0.248),
                                    ("Hydrogen", 0.094),
                                    ("Iron", 0.089)))


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
        
        # Get steel support volume and place it
        steel_builder = self.get_builder("steelsupport")
        steel_vol = steel_builder.get_volume()

        # Calculate position (from PERL positioning logic)
        steel_pos = geom.structure.Position(
            "steel_support_pos",
            x=Q("0cm"),
            y=Q("0cm"), 
            z=Q("0cm"))
            
        steel_place = geom.structure.Placement(
            "steel_support_place",
            volume=steel_vol,
            pos=steel_pos)
            
        det_enc_vol.placements.append(steel_place.name)



        
        return
