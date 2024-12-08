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

    # Define default parameters that can be overridden in configuration
    defaults = dict(
        pmt_TPB = [11,12,13,14,23,24],
        pmt_left_rotated = [11,12,13,14], 
        pmt_right_rotated = [21,22,23,24],
        
        # Basic dimensions
        pmt_y_positions = [405.3, 170.0, 0, -170.0, -405.3],
        pmt_z_positions = [306.0, 204.0, -204.0, -306.0, 68.1, 0],
        
        # Horizontal PMT positions
        horizontal_pmt_pos_bot = -301.7,
        horizontal_pmt_pos_top = -225.9,
        horizontal_pmt_z = 228.9,
        horizontal_pmt_y = 221.0,
        
        # PMT dimensions
        pmt_radius = Q("6.5*2.54cm"),  
        pmt_height = Q("11.1*2.54cm") - Q("1.877*2.54cm"),
        pmt_coating_thickness = Q("0.2mm")
    )

    def configure(self, **kwargs):
        # Update defaults with any overrides from configuration
        self.params = self.defaults.copy()
        self.params.update(kwargs)
        
        # Generate all PMT positions
        self.generate_pmt_positions()


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