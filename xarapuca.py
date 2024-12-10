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

    def configure(self, xarapuca_parameters=None, cathode_parameters=None, **kwargs):
        """Configure the X-ARAPUCA geometry.
        
        Args:
            xarapuca_parameters: Dictionary containing X-ARAPUCA parameters
            cathode_parameters: Dictionary containing cathode parameters
            **kwargs: Additional configuration parameters
        """
        print('Configure XARAPUCA')
        if hasattr(self, '_configured'):
            return
        
        # Store parameters
        if xarapuca_parameters:
            self.params = xarapuca_parameters
        if cathode_parameters:
            self.cathode = cathode_parameters

        # Calculate additional parameters
        if self.params and self.cathode:
            # Calculate derived parameters
            self.params['FCToArapucaSpaceLat'] = Q('65cm') + self.params['ArapucaOut_y']
            
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
        # if not self.params:
        #     raise RuntimeError("XARAPUCABuilder not configured")

        # # Create the main X-ARAPUCA shapes
        # main_shape = geom.shapes.Box(self.name + '_shape',
        #                            dx=self.params['ArapucaOut_x']/2.0,
        #                            dy=self.params['ArapucaOut_y']/2.0,
        #                            dz=self.params['ArapucaOut_z']/2.0)

        # inner_shape = geom.shapes.Box(self.name + '_inner_shape',
        #                             dx=self.params['ArapucaIn_x']/2.0,
        #                             dy=self.params['ArapucaIn_y']/2.0,
        #                             dz=self.params['ArapucaIn_z']/2.0)

        # window_shape = geom.shapes.Box(self.name + '_window_shape',
        #                              dx=self.params['ArapucaAcceptanceWindow_x']/2.0,
        #                              dy=self.params['ArapucaAcceptanceWindow_y']/2.0,
        #                              dz=self.params['ArapucaAcceptanceWindow_z']/2.0)

        # # Create the main volume
        # main_lv = geom.structure.Volume(self.name + '_volume',
        #                               material='G10',
        #                               shape=main_shape)

        # self.add_volume(main_lv)