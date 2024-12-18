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
        self.DP_CRT_switch = None  # Add this line
        self.HD_CRT_switch = None  # Add this line

    def configure(self, crt_parameters=None, steel_parameters=None, 
                 OriginXSet=None, OriginYSet=None, OriginZSet=None,
                 DP_CRT_switch=None, HD_CRT_switch=None,  # Add these lines
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
            DP_CRT_switch (bool): Flag to control DP CRT switch
            HD_CRT_switch (bool): Flag to control HD CRT switch
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

        # Store CRT switch settings
        self.DP_CRT_switch = DP_CRT_switch
        self.HD_CRT_switch = HD_CRT_switch

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
            # US Top Left configs
            ('USTopLeft', 'USTopLeftBa', [-1, -1, 1], "rPlus90AboutX", 0),
            ('USTopLeft', 'USTopLeftBa', [1, -1, 1], "rPlus90AboutX", 1),
            ('USTopLeft', 'USTopLeftFr', [-1, -1, 1], "rMinus90AboutYMinus90AboutX", 2),
            ('USTopLeft', 'USTopLeftFr', [-1, 1, 1], "rMinus90AboutYMinus90AboutX", 3),
            # US Bottom Left configs
            ('USBotLeft', 'USBotLeftFr', [-1, 1, 1], "rPlus90AboutX", 4),
            ('USBotLeft', 'USBotLeftFr', [1, 1, 1], "rPlus90AboutX", 5),
            ('USBotLeft', 'USBotLeftBa', [-1, -1, 1], "rMinus90AboutYMinus90AboutX", 6),
            ('USBotLeft', 'USBotLeftBa', [-1, 1, 1], "rMinus90AboutYMinus90AboutX", 7),
            # US Top Right configs
            ('USTopRight', 'USTopRightFr', [-1, -1, 1], "rPlus90AboutX", 8),
            ('USTopRight', 'USTopRightFr', [1, -1, 1], "rPlus90AboutX", 9),
            ('USTopRight', 'USTopRightBa', [1, -1, 1], "rMinus90AboutYMinus90AboutX", 10),
            ('USTopRight', 'USTopRightBa', [1, 1, 1], "rMinus90AboutYMinus90AboutX", 11),
            # US Bottom Right configs 
            ('USBotRight', 'USBotRightBa', [-1, 1, 1], "rPlus90AboutX", 12),
            ('USBotRight', 'USBotRightBa', [1, 1, 1], "rPlus90AboutX", 13),
            ('USBotRight', 'USBotRightFr', [1, -1, 1], "rMinus90AboutYMinus90AboutX", 14),
            ('USBotRight', 'USBotRightFr', [1, 1, 1], "rMinus90AboutYMinus90AboutX", 15),
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
        
        # Create basic shapes first
        if self.HD_CRT_switch:
            # Create HD CRT basic shapes
            crt_paddle = geom.shapes.Box(
                "CRTPaddle",
                dx=self.crt['CRTPaddleWidth']/2,
                dy=self.crt['CRTPaddleHeight']/2,
                dz=self.crt['CRTPaddleLength']/2)

            crt_module = geom.shapes.Box(
                "CRTModule", 
                dx=self.crt['CRTModWidth']/2,
                dy=self.crt['CRTModHeight']/2,
                dz=self.crt['CRTModLength']/2)

            # Create volumes for HD CRT modules
            for imod in range(16):
                modnum = imod + 1
                
                # Create U-side modules
                for i in range(64):
                    paddleid = f"U{modnum}_{i+1}"
                    # Create paddle volume
                    paddle_vol = geom.structure.Volume(
                        f"volAuxDetSensitive_CRTPaddle_{paddleid}",
                        material="Polystyrene",
                        shape=crt_paddle)
                    self.add_volume(paddle_vol)
                    
                # Create module volume
                mod_vol_u = geom.structure.Volume(
                    f"volAuxDet_CRTModule_U{modnum}",
                    material="Air",
                    shape=crt_module)

                # Place paddles inside module
                for i in range(32):
                    paddle_x1 = -self.crt['CRTModWidth']/2 + \
                            self.crt['CRTPaddleWidth']*(i + 0.5)
                    paddle_x2 = -self.crt['CRTModWidth']/2 + \
                            self.crt['CRTPaddleWidth']*(i + 1)
                    paddle_y1 = self.crt['CRTPaddleHeight']/2
                    paddle_y2 = -self.crt['CRTPaddleHeight']/2
                    paddle_z = Q('0cm')

                    # Place first paddle
                    paddleid1 = f"U{modnum}_{i+1}"
                    pos1 = geom.structure.Position(
                        f"posCRTPaddleSensitive_{paddleid1}",
                        x=paddle_x1, y=paddle_y1, z=paddle_z)
                    place1 = geom.structure.Placement(
                        f"placePaddle_{paddleid1}",
                        volume=self.get_volume(f"volAuxDetSensitive_CRTPaddle_{paddleid1}"),
                        pos=pos1)
                    mod_vol_u.placements.append(place1.name)

                    # Place second paddle
                    paddleid2 = f"U{modnum}_{i+33}"
                    pos2 = geom.structure.Position(
                        f"posCRTPaddleSensitive_{paddleid2}",
                        x=paddle_x2, y=paddle_y2, z=paddle_z)
                    place2 = geom.structure.Placement(
                        f"placePaddle_{paddleid2}",
                        volume=self.get_volume(f"volAuxDetSensitive_CRTPaddle_{paddleid2}"),
                        pos=pos2)
                    mod_vol_u.placements.append(place2.name)

                # Add module volume to builder
                self.add_volume(mod_vol_u)

                # Do the same for D-side modules
                # Do the same for D-side modules
            for i in range(64):
                paddleid = f"D{modnum}_{i+1}"
                # Create paddle volume
                paddle_vol = geom.structure.Volume(
                    f"volAuxDetSensitive_CRTPaddle_{paddleid}",
                    material="Polystyrene",
                    shape=crt_paddle)
                self.add_volume(paddle_vol)

            # Create module volume
            mod_vol_d = geom.structure.Volume(
                f"volAuxDet_CRTModule_D{modnum}",
                material="Air",
                shape=crt_module)

            # Place paddles inside module
            for i in range(32):
                paddle_x1 = -self.crt['CRTModWidth']/2 + \
                           self.crt['CRTPaddleWidth']*(i + 0.5)
                paddle_x2 = -self.crt['CRTModWidth']/2 + \
                           self.crt['CRTPaddleWidth']*(i + 1)
                paddle_y1 = self.crt['CRTPaddleHeight']/2
                paddle_y2 = -self.crt['CRTPaddleHeight']/2
                paddle_z = Q('0cm')

                # Place first paddle
                paddleid1 = f"D{modnum}_{i+1}"
                pos1 = geom.structure.Position(
                    f"posCRTPaddleSensitive_{paddleid1}",
                    x=paddle_x1, y=paddle_y1, z=paddle_z)
                place1 = geom.structure.Placement(
                    f"placePaddle_{paddleid1}",
                    volume=self.get_volume(f"volAuxDetSensitive_CRTPaddle_{paddleid1}"),
                    pos=pos1,
                    rot="rIdentity")
                mod_vol_d.placements.append(place1.name)

                # Place second paddle
                paddleid2 = f"D{modnum}_{i+33}"
                pos2 = geom.structure.Position(
                    f"posCRTPaddleSensitive_{paddleid2}",
                    x=paddle_x2, y=paddle_y2, z=paddle_z)
                place2 = geom.structure.Placement(
                    f"placePaddle_{paddleid2}",
                    volume=self.get_volume(f"volAuxDetSensitive_CRTPaddle_{paddleid2}"),
                    pos=pos2,
                    rot="rIdentity")
                mod_vol_d.placements.append(place2.name)

            # Add module volume to builder
            self.add_volume(mod_vol_d)
                
        if self.DP_CRT_switch:
            # Create DP CRT shapes
            scint_box_top = geom.shapes.Box(
                "scintBox_Top",
                dx=self.crt['TopCRTDPPaddleHeight']/2,
                dy=self.crt['TopCRTDPPaddleLength']/2,
                dz=self.crt['TopCRTDPPaddleWidth']/2)
                
            scint_box_bottom = geom.shapes.Box(
                "scintBox_Bottom",
                dx=self.crt['BottomCRTDPPaddleHeight']/2,
                dy=self.crt['BottomCRTDPPaddleLength']/2,
                dz=self.crt['BottomCRTDPPaddleWidth']/2)

            module_top = geom.shapes.Box(
                "ModulescintBox_Top",
                dx=self.crt['TopCRTDPModHeight']/2,
                dy=self.crt['TopCRTDPModWidth']/2,
                dz=self.crt['TopCRTDPModLength']/2)
                
            module_bottom = geom.shapes.Box(
                "ModulescintBox_Bottom",
                dx=self.crt['BottomCRTDPModHeight']/2,
                dy=self.crt['BottomCRTDPModWidth']/2,
                dz=self.crt['BottomCRTDPModLength']/2)

            # Create DP CRT volumes
            top_paddle_vol = geom.structure.Volume(
                "volAuxDetSensitiveCRTDPPaddleTop",
                material="Polystyrene",
                shape=scint_box_top)
                
            bottom_paddle_vol = geom.structure.Volume(
                "volAuxDetSensitiveCRTDPPaddleBottom",
                material="Polystyrene", 
                shape=scint_box_bottom)

            # Create and populate top module
            top_module_vol = geom.structure.Volume(
                "volAuxDetCRTDPModuleTop",
                material="Air",
                shape=module_top)

            # Place paddles in top module
            pos_x = self.crt['TopCRTDPModHeight']/2 - \
                    self.crt['TopCRTDPPaddleHeight']/2
            for i in range(8):
                paddle_pos = geom.structure.Position(
                    f"posCRTPaddleSensitiveTop_{i}",
                    x=pos_x, y=Q('0mm'), z=Q('0mm'))
                place = geom.structure.Placement(
                    f"placeCRTDPTOP_{i}",
                    volume=top_paddle_vol,
                    pos=paddle_pos,
                    rot="rMinus90AboutX")
                top_module_vol.placements.append(place.name)
                pos_x -= self.crt['CRTDPPaddleSpacing']

            # Similar construction for bottom module
            # Create and populate bottom module
            bottom_module_vol = geom.structure.Volume(
                "volAuxDetCRTDPModuleBottom",
                material="Air",
                shape=module_bottom)

            # Place paddles in bottom module
            pos_x = self.crt['BottomCRTDPModHeight']/2 - \
                    self.crt['BottomCRTDPPaddleHeight']/2
            for i in range(8):
                paddle_pos = geom.structure.Position(
                    f"posCRTPaddleSensitiveBottom_{i}",
                    x=pos_x, y=Q('0mm'), z=Q('0mm'))
                place = geom.structure.Placement(
                    f"placeCRTDPBOTTOM_{i}",
                    volume=bottom_paddle_vol,
                    pos=paddle_pos,
                    rot="rMinus90AboutX",
                    copynumber=8+i)  # Note: bottom paddles start numbering from 8
                bottom_module_vol.placements.append(place.name)
                pos_x -= self.crt['CRTDPPaddleSpacing']


            # Add volumes to builder
            self.add_volume(top_module_vol)
            self.add_volume(bottom_paddle_vol)
