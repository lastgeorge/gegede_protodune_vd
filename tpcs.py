#!/usr/bin/env python
'''
TPC (Time Projection Chamber) builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q
import math
from collections import namedtuple


def line_clip(x0: float, y0: float, nx: float, ny: float, rcl: float, rcw: float) -> list:
    """Line clipping algorithm for rectangular boundary.
    
    Args:
        x0, y0: Starting point coordinates
        nx, ny: Direction vector components 
        rcl: Rectangle length
        rcw: Rectangle width
        
    Returns:
        List of intersection points [x1,y1,x2,y2]
    """
    if abs(nx) < 1e-4: return [x0, 0, x0, rcw]  # Vertical line
    if abs(ny) < 1e-4: return [0, y0, rcl, y0]  # Horizontal line
    
    # Check all edge intersections
    intersections = []
    edges = [
        (0, lambda x: y0 - x0 * ny/nx),           # Left edge
        (rcl, lambda x: y0 + (x-x0) * ny/nx),     # Right edge
        (x0 - y0 * nx/ny, lambda x: 0),           # Bottom edge
        (x0 + (rcw-y0) * nx/ny, lambda x: rcw)    # Top edge
    ]
    
    for x, get_y in edges:
        y = get_y(x)
        if 0 <= x <= rcl and 0 <= y <= rcw:
            intersections.extend([x, y])
            if len(intersections) == 4:
                break
                
    return intersections

def generate_wires(length, width, nch, pitch, theta_deg, dia, w1offx, w1offy):
    """
    Generate wire positions for a single CRU plane without splitting.
    This matches the original PERL gen_wires() function.
    """
    # Convert angle to radians
    theta = math.radians(theta_deg)
    
    # Wire and pitch direction unit vectors
    dirw = [math.cos(theta), math.sin(theta)]
    dirp = [math.cos(theta - math.pi/2), math.sin(theta - math.pi/2)]
    
    # Alpha is angle for pitch calculations
    alpha = theta if theta <= math.pi/2 else math.pi - theta
    
    # Calculate wire spacing
    dX = pitch / math.sin(alpha)
    dY = pitch / math.sin(math.pi/2 - alpha)
    
    # Starting point adjusted for direction
    orig = [w1offx, w1offy]
    if dirp[0] < 0:
        orig[0] = length - w1offx
    if dirp[1] < 0:
        orig[1] = width - w1offy
        
    # Generate wires
    winfo = []
    offset = 0  # Starting point determined by offsets
    
    for ch in range(nch):
        # Reference point for this wire
        wcn = [orig[0] + offset * dirp[0],
            orig[1] + offset * dirp[1]]
            
        # Get endpoints from line clipping
        endpts = line_clip(wcn[0], wcn[1], dirw[0], dirw[1], length, width)
        
        if len(endpts) != 4:
            print(f"Could not find endpoints for wire {ch}")
            offset += pitch
            continue
            
        # Recenter coordinates
        endpts[0] -= length/2
        endpts[2] -= length/2
        endpts[1] -= width/2 
        endpts[3] -= width/2
        
        # Calculate wire center
        wcn[0] = (endpts[0] + endpts[2])/2
        wcn[1] = (endpts[1] + endpts[3])/2
        
        # Calculate wire length
        dx = endpts[0] - endpts[2]
        dy = endpts[1] - endpts[3]

        wlen = (dx**2 + dy**2)**(0.5)

        # Store wire info
        wire = [ch, wcn[0], wcn[1], wlen] + endpts
        winfo.append(wire)
        
        offset += pitch
    
    return winfo



class TPCBuilder(gegede.builder.Builder):
    '''
    Build the TPC volumes including wire planes
    '''
    def __init__(self, name):
        super(TPCBuilder, self).__init__(name)
        
        # Initialize parameters as None
        self.params = None
        self.wire_planes = {'U': None, 'V': None}

        # Add the subbuilders
        for name, builder in self.builders.items():
            self.add_builder(name, builder)

    def configure(self, tpc_parameters=None, print_config=False, print_construct=False, **kwds):
        if print_config:
            print('Configure TPC <- Cryostat <- ProtoDUNE-VD <- World')
        if (hasattr(self, '_configured')):
            return 
        # Store the parameters
        if tpc_parameters:
            self.params = tpc_parameters

        # print(self.params)

        self.print_construct = print_construct



        self._configured = True


    


    def construct(self, geom):
        if self.print_construct:
            print('Construct TPC <- Cryostat <- ProtoDUNE-VD <- World')
        
        #print(self.params)

        # This creates full CRU planes that will be split later
        self.wire_planes['U'] = generate_wires(
            self.params['lengthPCBActive'],
            self.params['widthPCBActive'], 
            self.params['nChans']['Ind1'],
            self.params['wirePitch']['U'],
            self.params['wireAngle']['U'].to('deg').magnitude,
            self.params['padWidth'],
            self.params['offsetUVwire'][0],
            self.params['offsetUVwire'][1]
        )
        
        self.wire_planes['V'] = generate_wires(
            self.params['lengthPCBActive'],
            self.params['widthPCBActive'],
            self.params['nChans']['Ind2'],
            self.params['wirePitch']['V'],
            self.params['wireAngle']['V'].to('deg').magnitude, 
            self.params['padWidth'],
            self.params['offsetUVwire'][0],
            self.params['offsetUVwire'][1]
        )


