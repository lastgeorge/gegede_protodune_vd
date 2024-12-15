#!/usr/bin/env python
'''
xarapuca builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class XARAPUCABuilder(gegede.builder.Builder):
    '''
    Build the Xarapucas for ProtoDUNE-VD.
    '''

    def __init__(self, name):
        super(XARAPUCABuilder, self).__init__(name)
        self.params = None
        self.cathode = None

    def configure(self, xarapuca_parameters=None, cathode_parameters=None, print_config=False, print_construct=False, **kwargs):
        """Configure the X-ARAPUCA geometry.
        
        Args:
            xarapuca_parameters: Dictionary containing X-ARAPUCA parameters
            cathode_parameters: Dictionary containing cathode parameters
            print_config: Whether to print configuration info
            print_construct: Whether to print construct info
            **kwargs: Additional configuration parameters
        """
        if print_config:
            print('Configure XARAPUCA <- Cryostat <- ProtoDUNE-VD <- World')
        if hasattr(self, '_configured'):
            return
        
        # Store parameters
        if xarapuca_parameters:
            self.params = xarapuca_parameters
        if cathode_parameters:
            self.cathode = cathode_parameters

        self.print_construct = print_construct

        # Calculate additional parameters
        if self.params and self.cathode:
            
            
            # Calculate positions of the 4 arapucas with respect to the Frame center
            self.list_posx_bot = []
            self.list_posz_bot = []
            
            # First arapuca
            self.list_posx_bot.append(-2*self.cathode['widthCathodeVoid'] - 
                                    2.0*self.cathode['CathodeBorder'] + 
                                    self.params['GapPD'] + 
                                    0.5*self.params['ArapucaOut_x'])
            self.list_posz_bot.append(0.5*self.cathode['lengthCathodeVoid'] + 
                                    self.cathode['CathodeBorder'])
            
            # Second arapuca
            self.list_posx_bot.append(-self.cathode['CathodeBorder'] - 
                                    self.params['GapPD'] - 
                                    0.5*self.params['ArapucaOut_x'])
            self.list_posz_bot.append(-1.5*self.cathode['lengthCathodeVoid'] - 
                                    2.0*self.cathode['CathodeBorder'])
            
            # Third arapuca (mirror of second)
            self.list_posx_bot.append(-self.list_posx_bot[1])
            self.list_posz_bot.append(-self.list_posz_bot[1])
            
            # Fourth arapuca (mirror of first)
            self.list_posx_bot.append(-self.list_posx_bot[0])
            self.list_posz_bot.append(-self.list_posz_bot[0])

        self._configured = True

    def construct(self, geom):
        """Construct the X-ARAPUCA geometry."""
        if self.print_construct:
            print('Construct XARAPUCA <- Cryostat <- ProtoDUNE-VD <- World')
    
        # Create the main X-ARAPUCA shapes
        out_box = geom.shapes.Box("XARAPUCA_out_shape",
                                dx=self.params['ArapucaOut_x']/2.0,
                                dy=self.params['ArapucaOut_y']/2.0,
                                dz=self.params['ArapucaOut_z']/2.0)

        in_box = geom.shapes.Box("XARAPUCA_in_shape", 
                               dx=self.params['ArapucaIn_x']/2.0,
                               dy=self.params['ArapucaIn_y']/2.0,
                               dz=self.params['ArapucaIn_z']/2.0)

        # Create subtraction for wall shape
        xw_y = self.params['ArapucaOut_y'] / 2.0
        xw_pos = geom.structure.Position(
                self.name + "_xw_pos1",
                x=Q('0cm'),
                y=xw_y,
                z=Q('0cm'))
        
        wall_shape = geom.shapes.Boolean("XARAPUCA_wall_shape",
                           type='subtraction',
                           first=out_box,
                           second=in_box,
                           pos=xw_pos)

        # Create acceptance window shape 
        window_shape = geom.shapes.Box("XARAPUCA_window_shape",
                                     dx=self.params['ArapucaAcceptanceWindow_x']/2.0,
                                     dy=self.params['ArapucaAcceptanceWindow_y']/2.0,
                                     dz=self.params['ArapucaAcceptanceWindow_z']/2.0)

        # Create the volumes
        wall_vol = geom.structure.Volume("volXARAPUCAWall",
                                       material="G10",
                                       shape=wall_shape)

        window_vol = geom.structure.Volume("volXARAPUCAWindow", 
                                         material="LAr",
                                         shape=window_shape)
        
        # Make the sensitive window volume by adding auxiliary info
        window_vol.params.append(("SensDet","PhotonDetector"))

        # Add the volumes to the builder
        self.add_volume(wall_vol)
        self.add_volume(window_vol)

    def calculate_cathode_positions(self, idx, cathode_center_x, cathode_center_y, cathode_center_z):
        '''Calculate positions of X-ARAPUCAs over the cathode'''
        positions = []
        
        for i in range(4):
            # Calculate x,y,z position for each ARAPUCA
            # Use the existing position calculations from PERL
            x = cathode_center_x  
            if i == 0:
                y = -2*self.cathode['widthCathodeVoid'] - 2.0*self.cathode['CathodeBorder'] + self.params['GapPD'] + 0.5*self.params['ArapucaOut_x'] + cathode_center_y
                z = 0.5*self.cathode['lengthCathodeVoid'] + self.cathode['CathodeBorder'] + cathode_center_z
            elif i == 1:
                y = -self.cathode['CathodeBorder'] - self.params['GapPD'] - 0.5*self.params['ArapucaOut_x'] + cathode_center_y
                z = -1.5*self.cathode['lengthCathodeVoid'] - 2.0*self.cathode['CathodeBorder'] + cathode_center_z
            elif i == 2:
                y = -(-self.cathode['CathodeBorder'] - self.params['GapPD'] - 0.5*self.params['ArapucaOut_x']) + cathode_center_y
                z = -(-1.5*self.cathode['lengthCathodeVoid'] - 2.0*self.cathode['CathodeBorder']) + cathode_center_z
            else:
                y = -(-2*self.cathode['widthCathodeVoid'] - 2.0*self.cathode['CathodeBorder'] + self.params['GapPD'] + 0.5*self.params['ArapucaOut_x']) + cathode_center_y # Mirror of position 0
                z = -(0.5*self.cathode['lengthCathodeVoid'] + self.cathode['CathodeBorder']) + cathode_center_z # Mirror of position 0
                
            if (idx == 1 and i == 3):
                y = -(-self.cathode['CathodeBorder'] - self.params['GapPD'] - 0.5*self.params['ArapucaOut_x']) + cathode_center_y

            positions.append((x,y,z))
            
        return positions

    def calculate_lateral_positions(self, frame_center_x, frame_center_y, frame_center_z):
        '''Calculate positions of X-ARAPUCAs on lateral walls'''
        positions = []
        
        # Calculate positions using parameters similar to PERL script
        for i in range(8):
            x = frame_center_x
            
            if i < 4:
                y = frame_center_y
                if i == 0:
                    x += self.params['Upper_FirstFrameVertDist']
            else:
                y = frame_center_y + 2*self.cathode['widthCathode'] + 2*(self.params['CathodeFrameToFC'] + 
                    self.params['FCToArapucaSpaceLat'] - self.params['ArapucaOut_y']/2)
                if i == 4:
                    x += self.params['Upper_FirstFrameVertDist']
                    
            if i in [1,5]:
                x -= self.params['VerticalPDdist']
            elif i in [2,6]:
                x = frame_center_x - self.params['Lower_FirstFrameVertDist'] 
            elif i in [3,7]:
                x += self.params['VerticalPDdist']
                
            z = frame_center_z
            
            positions.append((x,y,z))
            
        return positions