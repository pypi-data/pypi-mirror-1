"""mems.instrument.server.inm200

Microscope control class for the Leica INM200 microscope.
"""

__revision__ = "$Id: inm200.py,v 1.21 2002/09/24 19:08:12 akuchlin Exp $"

from mems.instrument.server.microscope import LeicaMicroscope, command_loop


class INM200(LeicaMicroscope):

    # Gives the width and height of the camera's field of vision at 100X in
    # microns.
    SCALE_AT_100X = (180, 140)


def main():
    command_loop(INM200)
