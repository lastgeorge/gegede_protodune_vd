#!/usr/bin/env python
'''
CRT (Cosmic Ray Tagger) builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class CRTBuilder(gegede.builder.Builder):
    '''
    Build the Cosmic Ray Tagger (CRT) for ProtoDUNE-VD.
    Implements both HD-CRT and DP-CRT modules.
    '''

    def __init__(self, name):
        super(CRTBuilder, self).__init__(name)
        self.crt = None
        self.steel = None
        self.OriginXSet = None
        self.OriginYSet = None
        self.OriginZSet = None

    def configure(self, crt_parameters=None, steel_parameters=None, 
                 OriginXSet=None, OriginYSet=None, OriginZSet=None, 
                 print_config=False,  
                 print_construct=False,  # Add this line
                 **kwargs):
        """Configure the CRT geometry.
        
        Args:
            crt_parameters (dict): CRT parameters from config
            steel_parameters (dict): Steel support parameters
            OriginXSet (Quantity): X origin coordinate 
            OriginYSet (Quantity): Y origin coordinate
            OriginZSet (Quantity): Z origin coordinate
            print_config (bool): Flag to control printing
            print_construct (bool): Flag to control printing during construction
            **kwargs: Additional configuration parameters
        """
        if print_config:
            print('Configure CRT <- ProtoDUNE-VD <- World')
        # Add guard against double configuration
        if hasattr(self, '_configured'):
            return

        # Store parameters
        if crt_parameters:
            self.crt = crt_parameters
        if steel_parameters:
            self.steel = steel_parameters

        # Store origin coordinates
        self.OriginXSet = OriginXSet
        self.OriginYSet = OriginYSet 
        self.OriginZSet = OriginZSet

        self.print_construct = print_construct

        # Mark as configured
        self._configured = True

    def calculate_positions(self):
        '''Calculate all the CRT module positions'''
        
        self.posCRTDS_x = []
        self.posCRTDS_y = []
        self.posCRTDS_z = [] 
        self.posCRTDS_rot = []
        
        self.posCRTUS_x = []
        self.posCRTUS_y = []
        self.posCRTUS_z = []
        self.posCRTUS_rot = []

        # Helper function to calculate positions
        def add_DS_position(index, x, y, z, rot):
            self.posCRTDS_x.append(x)
            self.posCRTDS_y.append(y)
            self.posCRTDS_z.append(z)
            self.posCRTDS_rot.append(rot)

        def add_US_position(index, x, y, z, rot):
            self.posCRTUS_x.append(x)
            self.posCRTUS_y.append(y)
            self.posCRTUS_z.append(z)
            self.posCRTUS_rot.append(rot)

        # Define CRT module configurations
        ds_configs = [
            # Top Left
            ('DSTopLeft', 'DSTopLeftBa', [-1, -1, 1], "rPlus90AboutX", 0),
            ('DSTopLeft', 'DSTopLeftBa', [1, -1, 1], "rPlus90AboutX", 1),
            ('DSTopLeft', 'DSTopLeftFr', [-1, -1, 1], "rMinus90AboutYMinus90AboutX", 2),
            ('DSTopLeft', 'DSTopLeftFr', [-1, 1, 1], "rMinus90AboutYMinus90AboutX", 3),
            # Bottom Left
            ('DSBotLeft', 'DSBotLeftFr', [-1, 1, 1], "rPlus90AboutX", 4),
            ('DSBotLeft', 'DSBotLeftFr', [1, 1, 1], "rPlus90AboutX", 5),
            ('DSBotLeft', 'DSBotLeftBa', [-1, -1, 1], "rMinus90AboutYMinus90AboutX", 6),
            ('DSBotLeft', 'DSBotLeftBa', [-1, 1, 1], "rMinus90AboutYMinus90AboutX", 7),
            # Top Right
            ('DSTopRight', 'DSTopRightFr', [-1, -1, 1], "rPlus90AboutX", 8),
            ('DSTopRight', 'DSTopRightFr', [1, -1, 1], "rPlus90AboutX", 9),
            ('DSTopRight', 'DSTopRightBa', [1, -1, 1], "rMinus90AboutYMinus90AboutX", 10),
            ('DSTopRight', 'DSTopRightBa', [1, 1, 1], "rMinus90AboutYMinus90AboutX", 11),
            # Bottom Right
            ('DSBotRight', 'DSBotRightBa', [-1, 1, 1], "rPlus90AboutX", 12),
            ('DSBotRight', 'DSBotRightBa', [1, 1, 1], "rPlus90AboutX", 13),
            ('DSBotRight', 'DSBotRightFr', [1, -1, 1], "rMinus90AboutYMinus90AboutX", 14),
            ('DSBotRight', 'DSBotRightFr', [1, 1, 1], "rMinus90AboutYMinus90AboutX", 15),
        ]

        us_configs = [
            # Using similar pattern for upstream modules...
            ('USTopLeft', 'USTopLeftBa', [1, -1, 1], "rPlus90AboutX", 1),
            ('USTopLeft', 'USTopLeftFr', [-1, -1, 1], "rMinus90AboutYMinus90AboutX", 2),
            ('USTopLeft', 'USTopLeftFr', [-1, 1, 1], "rMinus90AboutYMinus90AboutX", 3),
            # Continue for other US positions...
        ]

        # Process downstream modules
        for base, z_pos, mods, rot, idx in ds_configs:
            x = (self.steel['posCryoInDetEnc']['x'] + self.crt['CRTSurveyOrigin_x'] + 
                 self.crt[f'CRT_{base}_x'] + 
                 mods[0] * (self.crt['ModuleLongCorr'] if abs(mods[0]) == 1 else self.crt['ModuleSMDist']))
            y = (self.steel['posCryoInDetEnc']['y'] + self.crt['CRTSurveyOrigin_y'] + 
                 self.crt[f'CRT_{base}_y'] + 
                 mods[1] * (self.crt['ModuleLongCorr'] if abs(mods[1]) == 1 else self.crt['ModuleSMDist']))
            z = (self.crt['CRTSurveyOrigin_z'] + 
                 self.crt[f'CRT_{z_pos}_z'] + 
                 mods[2] * self.crt['ModuleOff_z'])
            add_DS_position(idx, x, y, z, rot)

        # Process upstream modules
        for base, z_pos, mods, rot, idx in us_configs:
            x = (self.steel['posCryoInDetEnc']['x'] + self.crt['CRTSurveyOrigin_x'] + 
                 self.crt[f'CRT_{base}_x'] + 
                 mods[0] * (self.crt['ModuleLongCorr'] if abs(mods[0]) == 1 else self.crt['ModuleSMDist']))
            y = (self.steel['posCryoInDetEnc']['y'] + self.crt['CRTSurveyOrigin_y'] + 
                 self.crt[f'CRT_{base}_y'] + 
                 mods[1] * (self.crt['ModuleLongCorr'] if abs(mods[1]) == 1 else self.crt['ModuleSMDist']))
            z = (self.crt['CRTSurveyOrigin_z'] + 
                 self.crt[f'CRT_{z_pos}_z'] + 
                 mods[2] * self.crt['ModuleOff_z'])
            add_US_position(idx, x, y, z, rot)

        # Calculate Beam Spot position
        self.BeamSpot_x = self.steel['posCryoInDetEnc']['x'] + self.crt['CRTSurveyOrigin_x'] + self.crt['BeamSpotDSS_x'] + self.OriginXSet
        self.BeamSpot_y = self.steel['posCryoInDetEnc']['y'] + self.crt['CRTSurveyOrigin_y'] + self.crt['BeamSpotDSS_y'] + self.OriginYSet
        self.BeamSpot_z = self.steel['posCryoInDetEnc']['z'] + self.crt['CRTSurveyOrigin_z'] + self.crt['BeamSpotDSS_z'] + self.OriginZSet

    def construct(self, geom):
        if self.print_construct:
            print('Construct CRT <- ProtoDUNE-VD <- World')
        '''Construct the CRT geometry'''
        # TODO: Add CRT construction code
        pass
