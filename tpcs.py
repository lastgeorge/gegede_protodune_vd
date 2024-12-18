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


def split_wires(wires, width, theta_deg):
    """
    Split wires at y=0 line into two halves.
    
    Args:
        wires: List of wire info
        width: Width to split at
        theta_deg: Wire angle in degrees
        
    Returns:
        Tuple of (lower_wires, upper_wires)
    """
    yref = 0
    theta = math.radians(theta_deg)
    nx = math.cos(theta)
    ny = math.sin(theta)
    
    winfo1 = [] # Lower half
    winfo2 = [] # Upper half
    ich1 = 0
    ich2 = 0
    
    for wire in wires:
        x0 = wire[1]
        y0 = wire[2] 
        endpts = wire[4:8]
        
        # Find max/min y values
        y1 = min(endpts[1], endpts[3])
        y2 = max(endpts[1], endpts[3])
        
        # Wire fully in lower half
        if y2 < yref:
            wire1 = [ich1, x0, y0, wire[3]] + endpts
            winfo1.append(wire1)
            ich1 += 1
            continue
            
        # Wire fully in upper half    
        if y1 > yref:
            wire2 = [ich2, x0, y0, wire[3]] + endpts
            winfo2.append(wire2)
            ich2 += 1
            continue
        
        # Wire crosses yref - calculate intersection
        x = x0 + (yref - y0) * nx/ny
        
        # Split into two wires
        endpts1 = list(endpts)
        endpts2 = list(endpts)
        
        if endpts[1] < yref:
            endpts1[2] = x
            endpts1[3] = yref
            endpts2[0] = x
            endpts2[1] = yref
        else:
            endpts1[0] = x
            endpts1[1] = yref
            endpts2[2] = x
            endpts2[3] = yref
            
        # Create new wires with adjusted centers
        wcn1 = [(endpts1[0] + endpts1[2])/2,
                (endpts1[1] + endpts1[3])/2]
        dx = endpts1[0] - endpts1[2]
        dy = endpts1[1] - endpts1[3]
        wlen1 = (dx*dx + dy*dy)**(0.5)
        wire1 = [ich1] + wcn1 + [wlen1] + endpts1
        winfo1.append(wire1)
        ich1 += 1
        
        wcn2 = [(endpts2[0] + endpts2[2])/2,
                (endpts2[1] + endpts2[3])/2] 
        dx = endpts2[0] - endpts2[2]
        dy = endpts2[1] - endpts2[3]
        wlen2 = (dx*dx + dy*dy)**(0.5)
        wire2 = [ich2] + wcn2 + [wlen2] + endpts2
        winfo2.append(wire2)
        ich2 += 1
        
    # Adjust y positions relative to width
    for w in winfo1:
        w[5] += -0.25 * width  # y1
        w[7] += -0.25 * width  # y2
        w[2] = 0.5 * (w[5] + w[7])  # ycenter
        
    for w in winfo2:
        w[5] += 0.25 * width  # y1
        w[7] += 0.25 * width  # y2
        w[2] = 0.5 * (w[5] + w[7])  # ycenter
            
    return winfo1, winfo2

def flip_wires(wires):
    """Flip wire configuration 180 degrees for second CRU.
    
    Args:
        wires: Input wire configurations
        
    Returns:
        list: Flipped wire configurations
    """
    winfo = []
    for wire in wires:
        # Flip endpoints
        xn1 = -wire[4]  # -x1
        yn1 = -wire[5]  # -y1
        xn2 = -wire[6]  # -x2  
        yn2 = -wire[7]  # -y2

        # New center
        xc = 0.5*(xn1 + xn2)
        yc = 0.5*(yn1 + yn2)

        # Create flipped wire config
        new_wire = [wire[0], xc, yc, wire[3],
                    xn1, yn1, xn2, yn2]
        winfo.append(new_wire)

    return winfo

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


    def construct_crm(self, geom, quad):
        """Construct one CRM (Cold Readout Module) quadrant."""
        
        def make_box(name, dx, dy, dz):
            """Create a box shape with given dimensions"""
            return geom.shapes.Box(f"{name}_{quad}", dx=dx/2, dy=dy/2, dz=dz/2)
        
        def make_volume(name, shape, material="LAr", **params):
            """Create a volume with given shape and parameters"""
            return geom.structure.Volume(f"{name}_{quad}", material=material, shape=shape, **params)

        # Calculate dimensions
        dims = {
            'active': (
                self.params['driftTPCActive'],
                self.params['widthPCBActive'] / 2,
                self.params['lengthPCBActive']
            ),
            'tpc': (
                self.params['driftTPCActive'] + self.params['ReadoutPlane'],
                self.params['widthPCBActive'] / 2,
                self.params['lengthPCBActive']
            ),
            'plane': (
                self.params['padWidth'],
                self.params['widthPCBActive'] / 2,
                self.params['lengthPCBActive']
            )
        }

        # Create shapes
        shapes = {
            'active': make_box('CRMActive', *dims['active']),
            'tpc': make_box('CRM', *dims['tpc']),
            **{plane: make_box(f'CRM{plane}Plane', *dims['plane']) 
               for plane in ['U', 'V', 'Z']}
        }

        # Create volumes
        vols = {
            'active': make_volume('volTPCActive', shapes['active'], 
                                params=[
                                    ("auxiliary", ("SensDet", "SimEnergyDeposit")),
                                    ("auxiliary", ("StepLimit", "0.5*cm")),
                                    ("auxiliary", ("Efield", "500*V/cm"))
                                ]),
            'tpc': make_volume('volTPC', shapes['tpc']),
            **{f'plane_{p}': make_volume(f'volTPCPlane{p}', shapes[p]) 
               for p in ['U', 'V', 'Z']}
        }

        # Define placements
        placements = {
            'active': (-self.params['ReadoutPlane']/2, 0, 0),
            'plane_U': (0.5*dims['tpc'][0] - 2.5*self.params['padWidth'], 0, 0),
            'plane_V': (0.5*dims['tpc'][0] - 1.5*self.params['padWidth'], 0, 0),
            'plane_Z': (0.5*dims['tpc'][0] - 0.5*self.params['padWidth'], 0, 0)
        }

        # Place all volumes
        for name, (x, y, z) in placements.items():
            pos = geom.structure.Position(f"pos{name}{quad}_pos", x=x, y=Q('0cm'), z=Q('0cm'))
            place = geom.structure.Placement(f"pos{name.split('_')[-1]}{quad}", 
                                          volume=vols[name], 
                                          pos=pos)
            vols['tpc'].placements.append(place.name)

        return vols['tpc']

    def construct_top_crp(self, geom):
        """Construct the Cold Readout Plane (CRP).
        Creates and processes wire configurations for U,V views.
        """
        # CRP total dimensions
        CRP_x = self.params['driftTPCActive'] + self.params['ReadoutPlane']
        CRP_y = self.params['widthCRP']
        CRP_z = self.params['lengthCRP']

        if self.print_construct:
            print(f"CRP dimensions: {CRP_x} x {CRP_y} x {CRP_z}")

        # Generate wire configurations for first CRU
        if self.params.get('wires_on', 1):  # Check if wires are enabled
            # U wires
            winfo_u1 = generate_wires(
            self.params['lengthPCBActive'], 
            self.params['widthPCBActive'],
            self.params['nChans']['Ind1'],
            self.params['wirePitch']['U'],
            self.params['wireAngle']['U'].to('deg').magnitude,
            self.params['padWidth'],
            self.params['offsetUVwire'][0],
            self.params['offsetUVwire'][1])

            # V wires  
            winfo_v1 = generate_wires(
            self.params['lengthPCBActive'],
            self.params['widthPCBActive'], 
            self.params['nChans']['Ind2'],
            self.params['wirePitch']['V'],
            self.params['wireAngle']['V'].to('deg').magnitude,
            self.params['padWidth'],
            self.params['offsetUVwire'][0], 
            self.params['offsetUVwire'][1])

            # Generate flipped wires for second CRU
            winfo_u2 = flip_wires(winfo_u1)
            winfo_v2 = flip_wires(winfo_v1)

            # Split wires for each quadrant
            winfo_u1a, winfo_u1b = split_wires(winfo_u1, 
                               self.params['widthPCBActive'],
                               self.params['wireAngle']['U'])
            winfo_v1a, winfo_v1b = split_wires(winfo_v1,
                               self.params['widthPCBActive'],
                               self.params['wireAngle']['V'])

            winfo_u2a, winfo_u2b = split_wires(winfo_u2,
                               self.params['widthPCBActive'],
                               self.params['wireAngle']['U'])  
            winfo_v2a, winfo_v2b = split_wires(winfo_v2,
                               self.params['widthPCBActive'],
                               self.params['wireAngle']['V'])

            # Store wire configurations for CRM construction
            self.wire_configs = {
                'U': [winfo_u1a, winfo_u1b, winfo_u2a, winfo_u2b],
                'V': [winfo_v1a, winfo_v1b, winfo_v2a, winfo_v2b]
            }

            # Construct CRM volumes with wire configurations
            for quad in range(4):
                self.construct_crm(geom, quad)


    def construct(self, geom):
        if self.print_construct:
            print('Construct TPC <- Cryostat <- ProtoDUNE-VD <- World')
        
        #print(self.params)

        # Build top CRP
        self.construct_top_crp(geom)

        # # This creates full CRU planes that will be split later
        # self.wire_planes['U'] = generate_wires(
        #     self.params['lengthPCBActive'],
        #     self.params['widthPCBActive'], 
        #     self.params['nChans']['Ind1'],
        #     self.params['wirePitch']['U'],
        #     self.params['wireAngle']['U'].to('deg').magnitude,
        #     self.params['padWidth'],
        #     self.params['offsetUVwire'][0],
        #     self.params['offsetUVwire'][1]
        # )
        
        # self.wire_planes['V'] = generate_wires(
        #     self.params['lengthPCBActive'],
        #     self.params['widthPCBActive'],
        #     self.params['nChans']['Ind2'],
        #     self.params['wirePitch']['V'],
        #     self.params['wireAngle']['V'].to('deg').magnitude, 
        #     self.params['padWidth'],
        #     self.params['offsetUVwire'][0],
        #     self.params['offsetUVwire'][1]
        # )

        # # Construct each quadrant
        # for quad in range(4):
        #     tpc_vol = self.construct_crm(geom, quad)
        #     self.add_volume(tpc_vol)


