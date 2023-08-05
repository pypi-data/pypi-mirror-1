"""mems.instrument.server.fake_microscope

Code for a simulated microscope.
"""

__revision__ = "$Id: fake_microscope.py,v 1.17 2003/01/02 16:19:38 akuchlin Exp $"

from mems.instrument import protocols
from mems.instrument.server import shared_map
from mems.instrument.server.microscope import Microscope, command_loop

map = shared_map.map_open()

class FakeMicroscope(Microscope):
    "Stores the microscope's state"

    # Magnification at which the image will be displayed without
    # shrinking or growing its pixels.
    DEFAULT_MAGNIFICATION = 10

    def __init__ (self):
        Microscope.__init__(self)
        self.x = self.y = self.z = 0
        self.autofocus = 'on'
        self.magnification = 5
        self.mode = protocols.MODE_BRIGHTFIELD
        self.aperture = 1
        self.light = 0
        self.angle = 0
        shared_map.set_map(self)


    def get_state (self):
        shared_map.set_map(self)
        scale = float(self.magnification) / self.DEFAULT_MAGNIFICATION
        state = {'x':self.x+.001, 'y':self.y+.001, 'z':self.z + .0001,
                 'magnification': self.magnification,
                 'mode': self.mode, 'aperture':self.aperture,
                 'light': self.light,
                 'x_scale': 320/scale, 'y_scale':240/scale,
                 'angle':self.angle,
                 'autofocus': self.autofocus,
                }
        return state

    def do_move (self, **args):
        if args.get('autofocus') == 'on':
            args['z'] = 0
        elif args.get('z') != 0:
            args['autofocus'] = 'off'
        for attr, value in args.items():
            setattr(self, attr, value)
        self.angle = self.angle % 360

def main():
    command_loop(FakeMicroscope)
