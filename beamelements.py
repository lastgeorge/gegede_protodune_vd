#!/usr/bin/env python
'''
beamelements builder for ProtoDUNE-VD geometry 
'''

import gegede.builder
from gegede import Quantity as Q
import math

class BeamElementsBuilder(gegede.builder.Builder):
    '''
    Build the ProtoDUNE-VD beamelements
    '''

    def __init__(self, name):
        super(BeamElementsBuilder, self).__init__(name)
        self.beam = None
        self.FoamPadding = None
        self.steel = None
        self.cryo = None

    def calculate_beam_angles(self):
        """Calculate derived beam angle parameters"""
        
        # Convert angles to radians
        theta3XZ_rad = float(self.beam['theta3XZ'].to('rad').magnitude)
        thetaYZ_rad = float(self.beam['thetaYZ'].to('rad').magnitude)

        # Calculate beam angles
        BeamTheta3 = math.atan(math.sqrt(math.tan(theta3XZ_rad)**2 + 
                                       math.tan(thetaYZ_rad)**2))
        BeamPhi3 = math.atan(math.tan(thetaYZ_rad)/math.tan(theta3XZ_rad))

        # Store calculated angles
        self.beam['BeamTheta3'] = BeamTheta3
        self.beam['BeamPhi3'] = BeamPhi3
        self.beam['BeamTheta3Deg'] = math.degrees(BeamTheta3)
        self.beam['BeamPhi3Deg'] = math.degrees(BeamPhi3)

        # Calculate deltas
        self.beam['DeltaXZ3'] = math.tan(BeamTheta3)*math.cos(BeamPhi3)
        self.beam['DeltaYZ3'] = math.tan(BeamTheta3)*math.sin(BeamPhi3)

    def configure(self, steel_parameters=None, cryostat_parameters=None, 
                 beam_parameters=None, FoamPadding=None, 
                 print_config=False,  
                 print_construct=False,  # Add this line
                 **kwargs):
        """Configure beam parameters"""
        
        if print_config:
            print('Configure BeamElements <- ProtoDUNE-VD <- World')
        if hasattr(self, '_configured'):
            return

        self.beam = beam_parameters
        self.steel = steel_parameters
        self.cryo = cryostat_parameters
        self.FoamPadding = FoamPadding

        

        if self.beam and self.steel and self.cryo and self.FoamPadding:
            # Calculate derived beam angles
            self.calculate_beam_angles()

            # Calculate beam vacuum pipe radius
            self.beam['BeamVaPipeRad'] = self.beam['BeamPipeRad'] - Q('0.2cm')
            self.beam['BeamVaPipeLe'] = self.beam['BeamPipeLe']

            # Calculate positions and lengths
            cos_theta3 = math.cos(self.beam['BeamTheta3'])
            
            # Calculate beam plug parameters
            self.beam['BeamPlugUSAr'] = Q('1cm')/cos_theta3
            self.beam['BeamPlugLe'] = Q('188cm')/cos_theta3 - self.beam['BeamPlugUSAr']
            self.beam['BeamPlugNiLe'] = self.beam['BeamPlugLe'] - Q('0.59cm')/cos_theta3
            self.beam['BeamPlugNiPos_z'] = Q('0.59cm')/(2*cos_theta3)

            # Steel plate front face coordinates
            self.beam['BeamWStPlateFF_x'] = Q('634.2cm') - self.cryo['Cryostat_x']/2
            self.beam['BeamWStPlateFF_y'] = (self.cryo['Cryostat_y']/2 + 
                                            self.steel['SteelSupport_y'] + 
                                            self.FoamPadding)
            self.beam['BeamWStPlateFF_z'] = -(self.cryo['Cryostat_z']/2 + 
                                            self.FoamPadding + 
                                            self.steel['SteelPlate'])

            # Steel plate parameters
            self.beam['BeamWStPlateLe'] = self.steel['SteelPlate']/cos_theta3 + Q('0.001cm')
            self.beam['BeamWStPlate_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                        (self.steel['SteelPlate']/2)*self.beam['DeltaXZ3'])
            self.beam['BeamWStPlate_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                        (self.steel['SteelPlate']/2)*self.beam['DeltaYZ3'])
            self.beam['BeamWStPlate_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                        self.steel['SteelPlate']/2)

            # Foam removal parameters
            self.beam['BeamWFoRemLe'] = self.FoamPadding/cos_theta3 + Q('0.001cm')
            self.beam['BeamWFoRemPosDZ'] = self.steel['SteelPlate'] + self.FoamPadding/2
            self.beam['BeamWFoRem_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                        self.beam['BeamWFoRemPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamWFoRem_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                        self.beam['BeamWFoRemPosDZ']*self.beam['DeltaYZ3'])
            self.beam['BeamWFoRem_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                        self.beam['BeamWFoRemPosDZ'])

            # Steel support parameters
            self.beam['BeamWStSuLe'] = ((self.steel['SteelSupport_z'] - 
                                        self.steel['SteelPlate'])/cos_theta3 + Q('0.001cm'))
            self.beam['BeamWStSuPosDZ'] = -(self.steel['SteelSupport_z'] - 
                                        self.steel['SteelPlate'])/2
            self.beam['BeamWStSu_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                    self.beam['BeamWStSuPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamWStSu_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                    self.beam['BeamWStSuPosDZ']*self.beam['DeltaYZ3'])
            self.beam['BeamWStSu_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                    self.beam['BeamWStSuPosDZ'])

            # Foam window parameters
            self.beam['BeamWFoPosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding - 
                                        self.beam['BeamWFoLe']*cos_theta3/2)
            self.beam['BeamWFo_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                    self.beam['BeamWFoPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamWFo_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                    self.beam['BeamWFoPosDZ']*self.beam['DeltaYZ3'] + 
                                    self.steel['posCryoInDetEnc']['y'])
            self.beam['BeamWFo_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                    self.beam['BeamWFoPosDZ'])

            # Glass window parameters
            self.beam['BeamWGlPosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding - 
                                        (self.beam['BeamWFoLe'] + 
                                        self.beam['BeamWGlLe']/2)*cos_theta3)
            self.beam['BeamWGl_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                    self.beam['BeamWGlPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamWGl_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                    self.beam['BeamWGlPosDZ']*self.beam['DeltaYZ3'] + 
                                    self.steel['posCryoInDetEnc']['y'])
            self.beam['BeamWGl_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                    self.beam['BeamWGlPosDZ'])

            # Vacuum window parameters
            self.beam['BeamWVaPosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding - 
                                        (self.beam['BeamWFoLe'] + self.beam['BeamWGlLe'] + 
                                        self.beam['BeamPipeLe']/2)*cos_theta3)
            self.beam['BeamWVa_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                    self.beam['BeamWVaPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamWVa_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                    self.beam['BeamWVaPosDZ']*self.beam['DeltaYZ3'] + 
                                    self.steel['posCryoInDetEnc']['y'])
            self.beam['BeamWVa_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                    self.beam['BeamWVaPosDZ'])

            # Calculate beam plug parameters
            self.beam['BeamPlugPosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding + 
                                        self.cryo['SteelThickness'] + 
                                        self.beam['BeamPlugUSAr'] + 
                                        self.beam['BeamPlugLe']*cos_theta3/2)
            self.beam['BeamPlug_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                    self.beam['BeamPlugPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamPlug_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                    self.beam['BeamPlugPosDZ']*self.beam['DeltaYZ3'])
            self.beam['BeamPlug_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                    self.beam['BeamPlugPosDZ'])

            # Beam plug flange parameters
            self.beam['BePlFlangePosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding + 
                                        self.cryo['SteelThickness'] + 
                                        self.beam['BeamPlugUSAr'] + 
                                        self.beam['BeamPlugLe']*cos_theta3)
            self.beam['BePlFlange_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                        self.beam['BePlFlangePosDZ']*self.beam['DeltaXZ3'])
            self.beam['BePlFlange_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                        self.beam['BePlFlangePosDZ']*self.beam['DeltaYZ3'])
            self.beam['BePlFlange_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                        self.beam['BePlFlangePosDZ'] + Q('1.8cm'))

            # Beam plug membrane parameters
            self.beam['BeamPlugMembPosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding + 
                                            self.cryo['SteelThickness'])
            self.beam['BeamPlugMemb_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                        self.beam['BeamPlugMembPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamPlugMemb_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                        self.beam['BeamPlugMembPosDZ']*self.beam['DeltaYZ3'])
            self.beam['BeamPlugMemb_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                        self.beam['BeamPlugMembPosDZ'])
            
            self._configured = True

    def construct(self, geom, print_construct=False):  # Add this line
        if print_construct:
            print('Construct Beam Elements <- ProtoDUNE-VD <- World')
        # TODO: Add Beam Elements construction code