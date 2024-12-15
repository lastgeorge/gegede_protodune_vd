#!/usr/bin/env python
'''
PMTs builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class PMTBuilder(gegede.builder.Builder):
    '''
    Build the PMTs for ProtoDUNE-VD.
    Implements both thick and slim field shapers arranged vertically.
    '''

    def configure(self, 
                 pmt_parameters=None,
                 print_config=False,
                 print_construct=False,
                 **kwds):
        
        if print_config:
            print('Configure PMTs <- Cryostat <- ProtoDUNE-VD <- World')
        if hasattr(self, '_configured'):
            return

        if pmt_parameters:
            self.params = pmt_parameters
        
        # Generate all PMT positions
        self.generate_pmt_positions()
        
        self._configured = True
        self.print_construct = print_construct

    def generate_pmt_positions(self):
        '''Generate the full list of PMT positions'''
        self.pmt_positions = []
        
        # Helper to make position dictionary
        def make_pos(x=None, y=None, z=None):
            pos = {}
            if x is not None: pos['x'] = Q(f"{x}cm")
            if y is not None: pos['y'] = Q(f"{y}cm") 
            if z is not None: pos['z'] = Q(f"{z}cm")
            return pos

        y = self.params['pmt_y_positions']
        z = self.params['pmt_z_positions']

        # Vertical PMTs
        self.pmt_positions.extend([
            make_pos(y=y[4], z=z[4]),      # pos1 - y=-405.3, z=68.1
            make_pos(y=y[4], z=z[5]),      # pos2 - y=-405.3, z=0
            make_pos(y=y[0], z=z[5]),      # pos3 - y=405.3, z=0
            make_pos(y=y[0], z=z[4]),      # pos4 - y=405.3, z=68.1
            make_pos(y=y[1], z=z[1]),      # pos5 - y=170.0, z=204.0
            make_pos(y=y[2], z=z[1]),      # pos6 - y=0, z=204.0
            make_pos(y=y[3], z=z[1]),      # pos7 - y=-170.0, z=204.0
            make_pos(y=y[1], z=z[0]),      # pos8 - y=170.0, z=306.0
            make_pos(y=y[2], z=z[0]),      # pos9 - y=0, z=306.0
            make_pos(y=y[3], z=z[0]),      # pos10 - y=-170.0, z=306.0
            make_pos(y=y[1], z=z[2]),      # pos15 - y=170.0, z=-204.0
            make_pos(y=y[2], z=z[2]),      # pos16 - y=0, z=-204.0
            make_pos(y=y[3], z=z[2]),      # pos17 - y=-170.0, z=-204.0
            make_pos(y=y[1], z=z[3]),      # pos18 - y=170.0, z=-306.0
            make_pos(y=y[2], z=z[3]),      # pos19 - y=0, z=-306.0
            make_pos(y=y[3], z=z[3]),      # pos20 - y=-170.0, z=-306.0
        ])

        # Horizontal PMTs 
        htop = self.params['horizontal_pmt_pos_top']
        hbot = self.params['horizontal_pmt_pos_bot']
        hz = self.params['horizontal_pmt_z']
        hy = self.params['horizontal_pmt_y']

        self.pmt_positions.extend([
            make_pos(x=htop, y=hy, z=hz),        # pos11 - x=-225.9, y=221.0, z=228.9
            make_pos(x=hbot, y=hy, z=hz),        # pos12 - x=-301.7, y=221.0, z=228.9
            make_pos(x=htop, y=-hy, z=hz),       # pos13 - x=-225.9, y=-221.0, z=228.9  
            make_pos(x=hbot, y=-hy, z=hz),       # pos14 - x=-301.7, y=-221.0, z=228.9
            make_pos(x=htop, y=hy, z=-hz),       # pos21 - x=-225.9, y=221.0, z=-228.9
            make_pos(x=hbot, y=hy, z=-hz),       # pos22 - x=-301.7, y=221.0, z=-228.9
            make_pos(x=htop, y=-hy, z=-hz),      # pos23 - x=-225.9, y=-221.0, z=-228.9
            make_pos(x=hbot, y=-hy, z=-hz),      # pos24 - x=-301.7, y=-221.0, z=-228.9
        ])

    def construct(self, geom):
        if self.print_construct:
            print('Construct PMTs <- Cryostat <- ProtoDUNE-VD <- World')
        # ...existing code...