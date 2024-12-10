#!/usr/bin/env python
'''
Main builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

# Import the CryostatBuilder
from cryostat import CryostatBuilder
from foam import FoamBuilder
from steelsupport import SteelSupportBuilder
from beamelements import BeamElementsBuilder

class ProtoDUNEVDBuilder(gegede.builder.Builder):
    '''
    Build the ProtoDUNE-VD detector enclosure and components
    '''

    def __init__(self, name):
        super(ProtoDUNEVDBuilder, self).__init__(name)
        
        # Initialize parameters as None
        self.cryo = None 
        self.tpc = None
        self.steel = None
        self.cathode = None
        self.fieldcage = None
        self.pmt = None

        self.DetEncX = None
        self.DetEncY = None
        self.DetEncZ = None

        self.OriginXSet = None
        self.OriginYSet = None 
        self.OriginZSet = None

        # Add the subbuilders
        # for name, builder in self.builders.items():
        #     self.add_builder(name, builder)

    def configure(self, cryostat_parameters=None, tpc_parameters=None, 
                 steel_parameters=None, beam_parameters=None, crt_parameters=None,
                 cathode_parameters=None, xarapuca_parameters=None,  # Add this line
                 fieldcage_parameters=None,  # Add this line
                 pmt_parameters=None,  # Add this line
                 DetEncX=None, DetEncY=None, DetEncZ=None, FoamPadding=None, 
                 OriginXSet=None, OriginYSet=None, OriginZSet=None,  # Add these
                 **kwds):
        
        print('Configure ProtoDUNE-VD')
        # Add guard against double configuration
        if hasattr(self, '_configured'):
            return

        # Store the parameters
        self.DetEncX = DetEncX
        self.DetEncY = DetEncY 
        self.DetEncZ = DetEncZ
        self.FoamPadding = FoamPadding

        # Store Origin coordinates
        self.OriginXSet = OriginXSet
        self.OriginYSet = OriginYSet
        self.OriginZSet = OriginZSet
        
        if cryostat_parameters:
            self.cryo = cryostat_parameters
        if tpc_parameters:
            self.tpc = tpc_parameters
        if steel_parameters:
            self.steel = steel_parameters
        if cathode_parameters:
            self.cathode = cathode_parameters
        if xarapuca_parameters:  # Add this block
            self.xarapuca = xarapuca_parameters
        if fieldcage_parameters:  # Add this block
            self.fieldcage = fieldcage_parameters
        if pmt_parameters:  # Add this block
            self.pmt = pmt_parameters

        
        # Mark as configured
        self._configured = True

        # Pass parameters to sub builders
        for name, builder in self.builders.items():
            if name == 'beamelements':
                builder.configure(steel_parameters=self.steel,
                                cryostat_parameters=self.cryo,
                                beam_parameters=beam_parameters,
                                FoamPadding=self.FoamPadding,
                                **kwds)
            if name == 'cryostat':
                builder.configure(cryostat_parameters=self.cryo,
                                  tpc_parameters=self.tpc,
                                  cathode_parameters=self.cathode,
                                  xarapuca_parameters=self.xarapuca,  # Add this line
                                  fieldcage_parameters=self.fieldcage,  # Add this line
                                  pmt_parameters=self.pmt,  # Add this line
                                **kwds)
            if name == 'crt':
                builder.configure(crt_parameters=crt_parameters,
                                steel_parameters=self.steel,
                                OriginXSet=self.OriginXSet,  # Add these three lines
                                OriginYSet=self.OriginYSet,
                                OriginZSet=self.OriginZSet,
                                **kwds)
            if name == 'steelsupport':
                builder.configure(steel_parameters=self.steel,
                                **kwds)
            if name == 'foam':
                builder.configure(FoamPadding=self.FoamPadding,
                                **kwds)

    def construct(self, geom):
        '''
        Construct the geometry.
        '''     

        # Create the main volume
        main_shape = geom.shapes.Box(self.name + '_shape',
                                   dx=self.DetEncX,
                                   dy=self.DetEncY,
                                   dz=self.DetEncZ)
        
        main_lv = geom.structure.Volume(self.name, 
                                      material='Air',
                                      shape=main_shape)

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
        main_lv.placements.append(cryo_place.name)

        self.add_volume(main_lv)


