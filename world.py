#!/usr/bin/env python
'''
World builder for ProtoDUNE-VD
'''

import gegede.builder
from gegede import Quantity as Q

from protodune import ProtoDUNEVDBuilder

class WorldBuilder(gegede.builder.Builder):
    '''
    Build the world volume which will contain the full detector
    '''

    def __init__(self, name):
        super(WorldBuilder, self).__init__(name)
        
        # Initialize parameters as None
        self.cryo = None 
        self.tpc = None
        self.steel = None
        self.beam = None
        self.crt = None
        self.cathode = None  # Add this line
        self.fieldcage = None  # Add this line
        self.pmt = None  # Add this line

        # Add the subbuilders
        # for name, builder in self.builders.items():
        #     self.add_builder(name, builder)
    

    def configure(self, material='Air', width=None, height=None, depth=None, 
                 tpc_parameters=None, cryostat_parameters=None, 
                 steel_parameters=None, beam_parameters=None, crt_parameters=None,
                 cathode_parameters=None, xarapuca_parameters=None,  
                 fieldcage_parameters=None,  
                 pmt_parameters=None,  
                 FoamPadding=None, AirThickness=None, DP_CRT_switch=None, 
                 cathode_switch=True, fieldcage_switch=True, arapucamesh_switch=True,  # Add these lines
                 print_config=False,  
                 print_construct=False,  # Add this line
                 **kwds):
        self.material = material
        
        if print_config:
            print('Configure World')
        # Add guard against double configuration
        if hasattr(self, '_configured'):
            return

        # Add the parameters that were moved out
        self.FoamPadding = FoamPadding
        self.AirThickness = AirThickness
        self.DP_CRT_switch = DP_CRT_switch
        self.cathode_switch = cathode_switch  # Add this line
        self.fieldcage_switch = fieldcage_switch  # Add this line
        self.arapucamesh_switch = arapucamesh_switch  # Add this line

        # Process TPC parameters
        if tpc_parameters:
            # Create a dictionary from the string with proper Quantity objects
            eval_globals = {'Q': Q}
            self.tpc = eval(tpc_parameters, eval_globals)
            
            # Calculate derived TPC parameters
            self.tpc['widthCRP'] = self.tpc['widthPCBActive'] + 2 * self.tpc['borderCRP']
            self.tpc['lengthCRP'] = (2 * self.tpc['lengthPCBActive'] + 
                                   2 * self.tpc['borderCRP'] + 
                                   self.tpc['gapCRU'])

            # Active TPC dimensions based on CRP
            self.tpc['widthTPCActive'] = (self.tpc['nCRM_x']/2) * self.tpc['widthCRP'] 
            self.tpc['lengthTPCActive'] = (self.tpc['nCRM_z']/2) * self.tpc['lengthCRP']

            # Total readout plane thickness
            self.tpc['ReadoutPlane'] = self.tpc['nViews'] * self.tpc['padWidth']

        # Process Cryostat parameters
        if cryostat_parameters:
            eval_globals = {'Q': Q}
            self.cryo = eval(cryostat_parameters, eval_globals)
            
            # Calculate derived parameters
            self.cryo['xLArBuffer'] = (self.cryo['Argon_x'] - 
                                      self.tpc['driftTPCActive'] - 
                                      self.cryo['HeightGaseousAr'] - 
                                      self.tpc['ReadoutPlane'])
            
            self.cryo['Upper_xLArBuffer'] = (self.cryo['Upper_xLArBuffer_base'] - 
                                            self.tpc['ReadoutPlane'])
            
            self.cryo['Lower_xLArBuffer'] = (self.cryo['Lower_xLArBuffer_base'] - 
                                            self.tpc['ReadoutPlane'])
            
            self.cryo['yLArBuffer'] = (self.cryo['Argon_y'] - 
                                      self.tpc['widthTPCActive']) * 0.5
            
            self.cryo['zLArBuffer'] = (self.cryo['Argon_z'] - 
                                      self.tpc['lengthTPCActive']) * 0.5
            
            self.cryo['Cryostat_x'] = self.cryo['Argon_x'] + 2 * self.cryo['SteelThickness']
            self.cryo['Cryostat_y'] = self.cryo['Argon_y'] + 2 * self.cryo['SteelThickness']
            self.cryo['Cryostat_z'] = self.cryo['Argon_z'] + 2 * self.cryo['SteelThickness']


         # Process Steel Support parameters
        if steel_parameters:
            eval_globals = {'Q': Q}
            self.steel = eval(steel_parameters, eval_globals)

            # Calculate detector enclosure dimensions
            self.DetEncX = (self.cryo['Cryostat_x'] + 
                                    2*(self.steel['SteelSupport_x'] + self.FoamPadding) + 
                                    2*self.steel['SpaceSteelSupportToWall'])
            
            self.DetEncY = (self.cryo['Cryostat_y'] + 
                                    2*(self.steel['SteelSupport_y'] + self.FoamPadding) + 
                                    self.steel['SpaceSteelSupportToCeiling'])
            
            self.DetEncZ = (self.cryo['Cryostat_z'] + 
                                    2*(self.steel['SteelSupport_z'] + self.FoamPadding) + 
                                    2*self.steel['SpaceSteelSupportToWall'])

            # Calculate position parameters
            self.steel['posCryoInDetEnc'] = {'x': Q('0cm'), 
                                            'y': Q('0cm'), 
                                            'z': Q('0cm')}

            # Calculate steel structure positions
            self.steel['posTopSteelStruct'] = (self.cryo['Argon_y']/2 + 
                                            self.FoamPadding + 
                                            self.steel['SteelSupport_y'])
            
            self.steel['posBotSteelStruct'] = -(self.cryo['Argon_y']/2 + 
                                            self.FoamPadding + 
                                            self.steel['SteelSupport_y'])
            
            self.steel['posZBackSteelStruct'] = (self.cryo['Argon_z']/2 + 
                                                self.FoamPadding + 
                                                self.steel['SteelSupport_z'])
            
            self.steel['posZFrontSteelStruct'] = -(self.cryo['Argon_z']/2 + 
                                                self.FoamPadding + 
                                                self.steel['SteelSupport_z'])
            
            self.steel['posLeftSteelStruct'] = (self.cryo['Argon_x']/2 + 
                                            self.FoamPadding + 
                                            self.steel['SteelSupport_x'])
            
            self.steel['posRightSteelStruct'] = -(self.cryo['Argon_x']/2 + 
                                                self.FoamPadding + 
                                                self.steel['SteelSupport_x'])

            # Adjust for CRT if needed  
            if self.DP_CRT_switch == True:
                self.steel['posTopSteelStruct'] -= Q('29.7cm')
                self.steel['posBotSteelStruct'] += Q('29.7cm')

            # Calculate origin positions
            self.OriginZSet = (self.DetEncZ/2.0 -
                                    self.steel['SpaceSteelSupportToWall'] -
                                    self.steel['SteelSupport_z'] -
                                    self.FoamPadding -
                                    self.cryo['SteelThickness'] -
                                    self.cryo['zLArBuffer'])

            self.OriginYSet = (self.DetEncY/2.0 -
                                    self.steel['SpaceSteelSupportToCeiling']/2.0 -
                                    self.steel['SteelSupport_y'] -
                                    self.FoamPadding -
                                    self.cryo['SteelThickness'] -
                                    self.cryo['yLArBuffer'] -
                                    self.tpc['widthTPCActive']/2)

            self.OriginXSet = (self.DetEncX/2.0 -
                                    self.steel['SpaceSteelSupportToWall'] -
                                    self.steel['SteelSupport_x'] -
                                    self.FoamPadding -
                                    self.cryo['SteelThickness'] -
                                    self.cryo['xLArBuffer'] +
                                    Q('6.0cm')/2 +  # heightCathode/2
                                    self.cryo['Upper_xLArBuffer'])

        # Process beam parameters
        if beam_parameters:
            eval_globals = {'Q': Q}
            self.beam = eval(beam_parameters, eval_globals)

        # Process CRT parameters
        if crt_parameters:
            eval_globals = {'Q': Q}
            self.crt = eval(crt_parameters, eval_globals)

        if cathode_parameters:
            eval_globals = {'Q': Q}
            self.cathode = eval(cathode_parameters, eval_globals)

        if xarapuca_parameters:  # Add this block
            eval_globals = {'Q': Q}
            self.xarapuca = eval(xarapuca_parameters, eval_globals)
            # Calculate derived parameters
            self.xarapuca['FCToArapucaSpaceLat'] = Q('65cm') + self.xarapuca['ArapucaOut_y']

        if fieldcage_parameters:  # Add this block
            eval_globals = {'Q': Q}
            self.fieldcage = eval(fieldcage_parameters, eval_globals)

        if pmt_parameters:  # Add this block
            eval_globals = {'Q': Q}
            self.pmt = eval(pmt_parameters, eval_globals)

        self.print_construct = print_construct
        # Mark as configured
        self._configured = True

        # Pass parameters to sub builders
        for name, builder in self.builders.items():
            if name == 'detenclosure':
                builder.configure(cryostat_parameters=self.cryo,
                                  tpc_parameters=self.tpc,
                                  steel_parameters=self.steel,
                                  beam_parameters=self.beam,
                                  crt_parameters=self.crt,
                                  cathode_parameters=self.cathode,
                                  xarapuca_parameters=self.xarapuca,  
                                  fieldcage_parameters=self.fieldcage,  
                                  pmt_parameters=self.pmt,  
                                  DetEncX=self.DetEncX,
                                  DetEncY=self.DetEncY,
                                  DetEncZ=self.DetEncZ,
                                  FoamPadding=self.FoamPadding,
                                  OriginXSet=self.OriginXSet,
                                  OriginYSet=self.OriginYSet,
                                  OriginZSet=self.OriginZSet,
                                  cathode_switch=self.cathode_switch,  # Add this line
                                  fieldcage_switch=self.fieldcage_switch,  # Add this line
                                  arapucamesh_switch=self.arapucamesh_switch,  # Add this line
                                  print_config=print_config,
                                  print_construct=print_construct,  # Add this line
                                **kwds)

    # define materials ...
    def construct_materials(self, geom):
        """Define all materials used in the geometry"""
    
        if(self.print_construct):
            print('Define Materials')

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
        mixture_density = Q("0.001225g/cc") * self.steel["FracMassOfAir"] + \
                        Q("7.9300g/cc") * self.steel["FracMassOfSteel"]
                        
        air_steel_mix = geom.matter.Mixture("AirSteelMixture",
                                        density = mixture_density,
                                        components = (
                                            ("STEEL_STAINLESS_Fe7Cr2Ni", self.steel["FracMassOfSteel"]),
                                            ("Air", self.steel["FracMassOfAir"])))

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
        if self.print_construct:
            print('Construct World')
        # Define materials first
        self.construct_materials(geom)
        # ...existing code...

        # print("A", self.DetEncX, self.DetEncY, self.DetEncZ)    

        shape = geom.shapes.Box(self.name + '_shape', 
                              dx=self.DetEncX + 2*self.AirThickness,
                              dy=self.DetEncY + 2*self.AirThickness,
                              dz=self.DetEncZ + 2*self.AirThickness)
        
        volume = geom.structure.Volume(self.name + '_volume',
                                     material=self.material,
                                     shape=shape)
        
        self.add_volume(volume)

        
        pd_builder = self.get_builder("detenclosure")
        pd_vol = pd_builder.get_volume()

        # Create a placement for the cryostat in the detector enclosure
        # Place it at the center (0,0,0) since the PERL script shows posCryoInDetEnc=(0,0,0)
        pd_pos = geom.structure.Position(
            "pd_pos",
            x=self.OriginXSet, 
            y=self.OriginYSet,
            z=self.OriginZSet)
        
        pd_place = geom.structure.Placement(
            "pd_place",
            volume=pd_vol,
            pos=pd_pos)

        # Add the cryostat placement to the detector enclosure volume
        volume.placements.append(pd_place.name)


