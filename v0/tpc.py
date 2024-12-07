#!/usr/bin/env python
'''
TPC (Time Projection Chamber) builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class TPCBuilder(gegede.builder.Builder):
    '''
    Build the TPC volumes including wire planes
    '''
    
    def configure(self, 
                 # Channel counts per CRU
                 nChannelsInd1=476,
                 nChannelsInd2=476, 
                 nChannelsCol=584,  # 2*292
                 
                 # Wire plane parameters
                 wirePitchU=Q('0.765cm'),
                 wireAngleU=Q('150.0deg'),
                 wirePitchV=Q('0.765cm'),
                 wireAngleV=Q('30.0deg'),
                 wirePitchZ=Q('0.51cm'),
                 
                 # Wire plane offsets
                 offsetUVwire_0=Q('1.50cm'),
                 offsetUVwire_1=Q('0.87cm'),
                 
                 # Active CRU area
                 lengthPCBActive=Q('149.0cm'),
                 widthPCBActive=Q('335.8cm'),
                 gapCRU=Q('0.1cm'),
                 borderCRP=Q('0.6cm'),
                 
                 # CRM counts
                 nCRM_x=4,  # 2*2
                 nCRM_z=2,  # 1*2
                 
                 # Active volume dimensions
                 driftTPCActive=Q('338.5cm'),
                 
                 # Wire plane parameters
                 padWidth=Q('0.02cm'),
                 **kwds):

        self.nChannels = {
            'Ind1': nChannelsInd1,
            'Ind2': nChannelsInd2,
            'Col': nChannelsCol
        }
        
        # Wire plane parameters
        self.wirePitchU = wirePitchU
        self.wireAngleU = wireAngleU
        self.wirePitchV = wirePitchV
        self.wireAngleV = wireAngleV
        self.wirePitchZ = wirePitchZ
        
        # Wire plane offsets
        self.offsetUVwire = [offsetUVwire_0, offsetUVwire_1]
        
        # Active CRU area
        self.lengthPCBActive = lengthPCBActive
        self.widthPCBActive = widthPCBActive
        self.gapCRU = gapCRU
        self.borderCRP = borderCRP
        
        # CRM counts
        self.nCRM_x = nCRM_x
        self.nCRM_z = nCRM_z
        
        # Active volume dimensions
        self.driftTPCActive = driftTPCActive
        
        # Wire plane parameters
        self.padWidth = padWidth
        
        # Calculate derived dimensions
        self.nViews = len(self.nChannels)
        
        # CRP dimensions
        self.widthCRP = self.widthPCBActive + 2 * self.borderCRP
        self.lengthCRP = 2 * self.lengthPCBActive + 2 * self.borderCRP + self.gapCRU
        
        # Active TPC dimensions
        self.widthTPCActive = self.nCRM_x/2 * self.widthCRP
        self.lengthTPCActive = self.nCRM_z/2 * self.lengthCRP
        
        # Total readout plane thickness
        self.ReadoutPlane = self.nViews * self.padWidth

    @property 
    def dimensions(self):
        return [self.driftTPCActive, self.widthTPCActive, self.lengthTPCActive]