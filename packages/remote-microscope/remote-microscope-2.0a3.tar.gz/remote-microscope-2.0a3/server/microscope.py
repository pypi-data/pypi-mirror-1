"""mems.instrument.microscope

Base class containing common microscope code.
"""

import sys, time, logging

from mems.instrument import protocols
from mems.instrument.server import util
from mems.instrument.server.configuration import get_configuration

log = logging.getLogger('server')
uscope_log = logging.getLogger('hardware.microscope')

# Inactive time after which the light will be dimmed (measured in seconds)
LIGHTING_TIMEOUT = 5*60

class Microscope:

    def __init__ (self):
        pass

    def read_hardware_status(self):
        pass

    def get_state(self):
        raise NotImplementedError

    #####################################################################
    # subclasses shouldn't have to mess with the stuff below
    #####################################################################

    def update_network(self):
        args = self.get_state()
        msg = protocols.build_message_line('scope_state', **args)
        util.send_message('network_server', msg)



class LeicaMicroscope (Microscope):
    """
    Base serial port and microscope control class for the Leica 
    microscopes, for opening simple RS-232 connections, and for
    controlling the Ergoplan and LUDL devices to steer the optics and
    stage.
    """

    # Gives the width and height of the camera's field of vision at 100X
    # in microns.  Values for lower magnifications are computed from the
    # 100x values by scaling them.  According to Ray Malone of Leica,
    # one stage unit = 0.4 microns.

    SCALE_AT_100X = (None, None) # subclass must override

    # List of magnifications; this must be ordered in the same order as
    # the microscope handles them. 

    MAGNIFICATIONS = [5, 10, 20, 50, 100]

    def __init__(self):
        Microscope.__init__(self)
        from mems.instrument.hardware import leica
        self.scope = leica.Microscope() # the controller object
        self.scales = {}
        for i in self.MAGNIFICATIONS:
            x, y = self.SCALE_AT_100X
            factor = 100 / i
            self.scales[i] = x*factor, y*factor

    def get_state(self):
        scope = self.scope
        x_scale, y_scale = self.scales[scope.magnification]
        state = {'x':scope.x, 'y':scope.y, 'z':scope.z,
                 'magnification': scope.magnification,
                 'mode': scope.mode, 'aperture':scope.aperture,
                 'light': scope.light,
                 'x_scale': x_scale, 'y_scale':y_scale,
                 'angle':scope.angle,
                 'autofocus':scope.autofocus,
                }
        return state

    def do_move (self, **args):
        self.scope.set(**args)


def command_loop(microscope_class, *args, **kwargs):
    scope = microscope_class(*args, **kwargs)
    config = get_configuration()

    # Perform an initial check on the microscope's state
    scope.read_hardware_status()
    time.sleep(1)
    scope.update_network()
    last_activity = time.time()

    while 1:
        if util.has_input_waiting(sys.stdin, 10):
            line = sys.stdin.readline()
            if line == "": continue
            cmd, args = protocols.parse_message_line(line)

            log.debug('%s: Received command %s %r' % (__name__, cmd, args))

            if cmd == 'quit':
                log.info('%s: exiting' % __name__)
                break
            elif cmd == "move":
                scope.do_move(**args)
                scope.update_network()
                last_activity = time.time()
            else:
                log.error("%s: Unknown command %r args=%r"
                          % (__name__, cmd, args))

        else:
            scope.read_hardware_status()
            # scope.update_network()

            now = time.time()
            if (now - last_activity) > LIGHTING_TIMEOUT:
                # Dim the lights by 10%.  If it's less than 40%, turn the lights
                # off completely.
                state = scope.get_state()
                value = state['light']
                value = max(0, value-10)
                if value < 40:
                    value = 0
                scope.do_move(light=value)
                last_activity = now


