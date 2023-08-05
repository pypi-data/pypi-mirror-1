"""mems.instrument.server.ins1000

Microscope control class for the Leica INS1000 microscope.
"""

__revision__ = "$Id: ins1000.py,v 1.18 2002/09/24 19:08:12 akuchlin Exp $"

from mems.instrument.server.microscope import LeicaMicroscope, command_loop

class INS1000 (LeicaMicroscope):

    # Gives the width and height of the camera's field of vision at 100X in
    # microns.
    SCALE_AT_100X = (125, 98)


def main ():
    command_loop(INS1000)
