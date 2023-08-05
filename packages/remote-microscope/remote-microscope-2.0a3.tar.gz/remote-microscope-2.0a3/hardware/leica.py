"""mems.instrument.hardware.leica

Contains classes for manipulating Leica's microscope hardware.

"""

__revision__ = "$Id: leica.py,v 1.21 2002/11/13 14:59:34 akuchlin Exp $"

import os, select, string, struct, sys, time

from mems.instrument import protocols
from mems.instrument.hardware.serial_port import SerialPort
from mems.instrument.hardware.secs_i import SECS_I
from mems.instrument.server.configuration import get_configuration

# Display timing information
TIMING = 0

# X,Y coordinates of the center of rotation (varies from microscope to
# microscope).  XXX should remove this since it changes; instead 
# it should be stored in some kind of calibration file

ROTATION_X, ROTATION_Y = 0,0

# Exception raised if there's a problem with the scope
class InstrumentException:
    "Exception raised if anything goes wrong"
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return '<InstrumentException: %s>' % self.message

class LUDLController(SerialPort):
    """The LUDL controller is connected to just the microscope stage; 
    it therefore controls the X and Y coordinates, and theta (the
    rotation of the specimen).  Refer to the Leica manual titled "MAC
    2000 Programming" for the commands accepted by the controller.
    """

    def __init__(self, dev):
        SerialPort.__init__( self, dev )

    def send_cmd(self, s):
        "Send a command to the LUDL controller, checking for an error response"
        s = string.strip(s)
        os.write(self.fd, s+'\r')
        
        # Now that we've sent the command, read the scope's response.
        # Curiously, the LUDL seems to return the entire line, then delay
        # for a second before returning the final "\n".  This delay
        # isn't long enough to present any problems, though.
        response = ""
        while (1):
            read_list, dummy, dummy = select.select([self.fd], [], [], 0.0001)
            c = os.read(self.fd, 1)
            if c in '\n\r': break
            response = response + c
            
        response = string.split( response )
        
        # At this point, the response is a list, something like [":N",
        # "-1"] or [":A", "45"].  
        if response[0] == ':N':
            # Handle an error response
            errcode = string.atoi(response[1])
            if errcode == -1:
                raise InstrumentException, 'Unknown scope command: '+repr(s)
            elif errcode == -2:
                raise InstrumentException, 'Illegal point type or axis in: '+repr(s)
            elif errcode == -3:
                raise InstrumentException, 'Not enough parameters in: '+repr(s)
            elif errcode == -4:
                raise InstrumentException, 'Parameter out of range in: '+repr(s)
            elif errcode == -21:
                raise InstrumentException, 'Aborted by HALT command: '+repr(s)

        elif response[0] == ":A":
            # No error, so just return the rest of the response
            return response[1:]

        else:
            # The response begins with neither :N or :A; this
            # shouldn't happen.
            raise InstrumentException, ("Unknown microscope response to " +
                               repr(s) +": "+repr(response) )

# Constants for the Ergoplan controller.
# Constants that aren't actually used in the microscope server at this 
# time aren't present, even though they're listed in the documentation.

POS_ABS = 1         # Set a unit to an absolute value
READ_POS = 3        # Read the value of a unit
SWITCH_MOD = 4      # Enable/disable module
READ_MOD = 5        # Determine the enabled/disabled status of a module
READ_LFS = 10       # Read status of laser focusing system
SET_MICRO = 11      # Set various microscope parameters
READ_MICRO = 12     # Read the microscope parameters

# Unit numbers --- different units control different settings.
MICRO = 6           # General microscope settings
M_STOP = 10         # Darkfield setting
B_LAMPE = 13        # Lamp intensity
OBJ_REV = 14        # Objective revolver
A_BLENDE = 15       # Aperture
L_BLENDE = 16       # Field diaphragm (used when going to darkfield mode)
A_TEILER = 19       # ICR mode
W_PRISMA = 25       # ICR prism; 0=out, 1 - 32767 are positions
Z_TRIEB = 30        # Z-drive; the height of the stage
Z_END_O = 31        # Upper limit of Z-drive
Z_END_U = 32        # Lower limit of Z-drive
O_TRIEB = 33        # Adjust offset/drive
L_SIGNAL = 36       # Laser diode signal
SRCH_FOC = 38       # Laser autofocus
FOCUS = 39          # Another autofocus unit (used w/ READ_LFS)

class ErgoplanController(SerialPort, SECS_I):
    """Class for sending commands to the Ergoplan controller, which
    controls everything except the stage: the magnification being
    used, the Z-axis (raising/lowering the object), apertures,
    lighting, brightfield/darkfield/ICR.  Refer to the "Control
    Functions of the Ergoplan Microscope" document, in the folder
    titled "Microscope Protocols." """

    def __init__(self, filename):
        SerialPort.__init__(self, filename)
        SECS_I.__init__(self)

    def ergoplan_send(self, msg):
        self.send_message( msg )     # Send the message ...
        self.receive_message()       # ... and read the response
        return self.get_message()    # Return the response
    
    def enable(self, unit):
        "Enable a unit"
        msg = chr(SWITCH_MOD)  + chr(unit) + '\001'
        resp = self.ergoplan_send( msg )

    def disable(self, unit):
        "Disable a unit"
        msg = chr(SWITCH_MOD)  + chr(unit) + '\000'
        resp = self.ergoplan_send( msg )

    def isEnabled(self, unit):
        msg = chr(READ_MOD)  + chr(unit) + '\000'
        msg = self.ergoplan_send(msg)
        return msg[2] == '\001'

    def get(self, unit):
        "Return the integer value for a unit"
        msg = chr(READ_POS)  + chr(unit) + '\000'*7
        msg = self.ergoplan_send(msg)
        mode, value, speed = struct.unpack('>BIH', msg[2:9])
        if value > sys.maxint: return value
        else: return int(value)

    def set(self, unit, value):
        "Set a unit to the given value; an absolute, not relative change."
        value = int(value)
        msg = chr(POS_ABS) + chr(unit) + struct.pack('>I', value)
        msg = self.ergoplan_send(msg)
        # XXX should check the result here in some way
        
# List of magnifications; this must be ordered in the same order as
# the microscope handles them.  Only the scale value at 100x has been
# measured; values for lower magnifications are computed from the 100x 
# values by scaling them.  
 
MAGNIFICATIONS = [5, 10, 20, 50, 100]

class Microscope:
    """Class for controlling the microscope, reading its status, and
    grabbing images from it.

    Methods:
    move                 Move the microscope
    read_hardware_status Update the attributes from the microscope hardware
    close                Close RS-232 connections and douse the light
    
    Attributes:
    x,y,z,angle         Microscope stage position
    z_min, z_max        Limits of microscope motion
    magnification                 Magnification (one of 5,10,20,50,100)
    mode                Mode (one of 'brightfield', 'darkfield', 'ICR')
    aperture            Aperture setting (1 through 6)
    light               Lighting intensity (0-255)
    autofocus           Boolean denoting whether autofocus is on/off
    """
    
    # Again according to Ray Malone, for the Z-axis one unit = 0.018 microns.
    Z_CONVERSION = 0.018

    # 60,000 angular units makes up one full rotation.
    ANGLE_CONVERSION = 60000
    
    def __init__(self):
        "Open serial port connections and initialize instance variables."

        self.z_min, self.z_max = -5000, 5000
        self.z_autofocus = 0
                
        # Set some starting values; they should all get overwritten by 
        # the called to read_hardware_status() later.
        self.x = self.y = self.z = 0.0

        self.angle = 0
        self.magnification = 5
        self.mode = protocols.MODE_BRIGHTFIELD
        self.aperture=1 ; self.autofocus = False
        self.light=0
        self.prism_pos = { 5: 12000, 10:12505, 20:36000, 50:35092, 100:36000 }

        # Create instances which will handle the connection.
        self.__stage_port = LUDLController('/dev/stage')
        self.__microscope_port = ErgoplanController('/dev/optics')

        # If the centering option was specified, home the stage at
        # this point. 
        config = get_configuration()
        if config.server.center_stage:
            self.center_stage()
            
        # Put the lighting under automatic control, and enable autofocus
        self.__microscope_port.enable(B_LAMPE)
        self.set(autofocus = 'on')

    def center_stage(self):
        """Center the microscope's stage, calibrating it by sweeping it to
        its extreme limits of movement, and then setting the center of
        that range to 0,0."""
        
        # Ensure autofocus is disabled
        self.set(autofocus = 'off')

        config = get_configuration()
        if config.get_debug():
            print 'Centering the stage...'

        resp = self.__stage_port.send_cmd('center x=30000 y=30000')

        # Repeatedly get the stage's coordinates, and wait until
        # they've settled down to a fixed value.  This means that the
        # centering process is complete.
        
        last = []
        while 1:
            resp = self.__stage_port.send_cmd('where x y')
            if config.get_debug():
                sys.stdout.write(string.rjust( resp[0], 8 ) + ' '
                                 + string.rjust( resp[1], 8 )
                                 + 17*'\b')
                sys.stdout.flush()
            if (resp == last and abs(int(resp[0])) < 1000 and
                abs(int(resp[0]))<1000 ):
                break
            last = resp

        # Set the coordinates of the current location to 0,0
        self.__stage_port.send_cmd('here x=0 y=0')
        if config.get_debug():
            print 17*' ' + 17*'\b' + 'Centering completed'

            
    def read_hardware_status(self):
        """Set the microscope's attributes from what the hardware reports."""

        if TIMING:
            t1 = time.time()
        resp = self.__stage_port.send_cmd('where x y')
        self.x, self.y, = int(resp[0]), int(resp[1])
        config = get_configuration()
        if config.server.rotate_stage:
            resp = self.__stage_port.send_cmd('where b')
            angle = int(resp[0]) * 360 / self.ANGLE_CONVERSION
            self.angle = round(angle % 360, 1)
            
        if TIMING:
            t2 = time.time()
            print '*** time to get x,y,b coordinates:', t2-t1

        z = self.__microscope_port.get(Z_TRIEB)
        self.z = (z - self.z_autofocus) * self.Z_CONVERSION
        
        # If the autofocus is enabled, assume that z_autofocus is
        # equal to the current Z-position of the stage.
        if self.autofocus:
            self.z_autofocus = z ; self.z = 0
            # Compute the upper and lower limits of safe Z coordinates.
            # The lower limit is always zero, because it's always safe to
            # move the stage down.  The upper limit is derived this way:
            # the 100x lens has a working distance of .3mm = 300 microns.
            # We'll give the user 50 microns of freedom, which is
            # 50/.018 = 2777 units.
            self.z_min = 0
            self.z_max = self.z_autofocus + int(50 / self.Z_CONVERSION)
            if config.get_debug():
                print 'setting zmin, z_auto, zmax=',
                print self.z_min, self.z_autofocus, self.z_max

        if TIMING:
            t3 = time.time()
            print '*** time to get z coordinate:', t3-t2

        msg = chr(READ_MICRO) + chr(MICRO) + 11*'\0'
        resp = self.__microscope_port.ergoplan_send(msg)

        # Get the microscope's mode:
        # Check if darkfield illumination is on; then we're in darkfield mode
        if ord(resp[2]) == 1:
            self.mode = protocols.MODE_DARKFIELD
        # Otherwise, check field diaphragm position to see if we're in ICR mode
        elif self.__microscope_port.get( A_TEILER ) == 2:
            self.mode = protocols.MODE_ICR
        else:
            self.mode = protocols.MODE_BRIGHTFIELD

        self.aperture = ord(resp[5])    # Get aperture setting
        mag_index = ord(resp[6])-2      # Get the selected objective
        self.magnification = MAGNIFICATIONS[ mag_index ]
        if TIMING:
            t4 = time.time()
            print '*** time to get settings:', t4-t3

        # Get light intensity
        self.light = self.__microscope_port.get(B_LAMPE) * 100 / 255

        if TIMING:
            t5 = time.time()
            print '*** time to get light intensity:', t5-t4

    def set(self, **kw):
        """Move the microscope stage relative to the
        current position, and update the microscope's status."""

        config = get_configuration()

        start_cmd = time.time()
        delay = 0.0                     # Time to wait at the end
        params_used = []

        # Set the light intensity
        if kw.has_key('light'):
            params_used.append( 'light' )
            light = kw['light']
            if self.light != light:
                light = min(light, 100)
                self.__microscope_port.set(B_LAMPE, light*255/100)

                # When the light intensity is changed, it takes a bit of
                # time for the light to heat up or cool down to reach the
                # new intensity.  I'm not sure how long it takes, but
                # let's set the delay to 2sec for going from 0 to 100.
                delay = delay + abs(light - self.light) * 2.0 / 100
                self.light = kw['light']
                        
        # Create the movement command for the stage; this requires
        # just X and Y coordinates, because the INS1000 doesn't
        # support rotating the wafer.
        cmd = ""
        
        x = kw.get('x')
        if x is None: 
            x = self.x
        else:
            params_used.append( 'x' )
            cmd = cmd + 'x=' + str(int(x)) + ' '

        y = kw.get('y')
        if y is None: y = self.y
        else:
            params_used.append( 'y' )
            cmd = cmd + 'y='+str(int(y)) + ' '

        # Set the angle
        # XXX should rearrange x/y coordinate depending on the angle
        if kw.has_key('angle') and config.server.rotate_stage:
            angle = kw['angle'] ; params_used.append('angle')
            angle = int(angle * self.ANGLE_CONVERSION / 360)
            if config.get_debug():
                print 'Setting angle coordinate to', angle
            cmd = cmd + 'b=' + str(angle) + ' '

        if cmd != "":
            # If a coordinate was actually changed, send a movement command
            # to the stage.
            self.__stage_port.send_cmd( "move " + cmd )
            
        # Set the Z-coordinate
        if kw.has_key('z'):
            z = kw['z'] ; params_used.append('z')
            z = int(z / self.Z_CONVERSION + self.z_autofocus)
            if config.get_debug():
                print 'Setting z coordinate to', z

            # Clip z to be between the allowed limits
            if not (self.z_min <= z < self.z_max):
                z = min(z, self.z_max)
                z = max(z, self.z_min)
            if z != self.z:
                # If we're actually changing the coordinate, turn off
                # autofocus and set it.
                self.set(autofocus = 'off')
                self.__microscope_port.set(Z_TRIEB, z)    # Set Z coordinate
                self.z = kw['z']
            
        # Set the magnification.

        if kw.has_key('magnification'):
            magnification = kw['magnification'] ; params_used.append('magnification')
            assert magnification in [5,10,20,50,100]
            if magnification != self.magnification:
                # This is only done if the magnification is actually being 
                # changed.
                try:
                    index = MAGNIFICATIONS.index( magnification )
                except ValueError:
                    raise InstrumentException, \
                          "Illegal magnification: "+str(magnification)
                else:
                    if magnification > self.magnification:
                        # For the safety of the objective, when increasing the
                        # magnification, we disable the autofocus, and move the
                        # Z-coord to 0 before changing objectives.
                        self.set(autofocus = 'off')
                        self.__microscope_port.set(Z_TRIEB, 0)    # Move to Z=0

                        # Sleep for a second to give the stage time to
                        # move down a bit.
                        time.sleep(1)

                    # Rotate the objective turret
                    self.__microscope_port.set(OBJ_REV, index + 2)
                    # Set the aperture, too.
                    if self.mode != 'Darkfield':
                        self.__microscope_port.set(A_BLENDE, self.aperture)
                    else:
                        self.__microscope_port.set(A_BLENDE, 6)

                    # Be sure to enable autofocus; it may not be turned on for
                    # the new magnification.
                    self.set(autofocus = 'on')
                    self.__microscope_port.enable(B_LAMPE)

                    self.magnification = magnification

        # Set the selected aperture.
        
        if kw.has_key('aperture'):
            aperture = kw['aperture'] ; params_used.append( 'aperture' )
            assert 1 <= aperture <= 5
            if self.aperture != aperture:
                try:
                    aperture = int(aperture)
                except ValueError: pass
                else:
                    if not (1<= aperture <=5):
                        raise ValueError, "Aperture must be between 1 and 5"
                    # Don't change the aperture in dark field mode; it has to
                    # remain set at 6.
                    if self.mode != 'Darkfield':
                        self.__microscope_port.set(A_BLENDE, aperture)
                    self.aperture = aperture

        # Set the viewing mode: brightfield, darkfield, ICR.

        if kw.has_key('mode'):
            mode = string.lower(kw['mode'])
            params_used.append('mode')
            assert mode in [protocols.MODE_BRIGHTFIELD,
                            protocols.MODE_DARKFIELD,
                            protocols.MODE_ICR]
        
            if mode != self.mode:
                # To switch modes, we need to send the READ_MICRO command
                # (page 35 of the Ergoplan docs), modify the state a bit,
                # and send a SET_MICRO command.
                state = self.__microscope_port.ergoplan_send(chr(12)+chr(6)+9*'0')
                state = map(None, state)  # Expand string into a list
                if mode == 'icr':
                    mode=='ICR'
                    # Enable ICR, and disable the darkfield unit
                    state[2] = chr(0)    # Brightfield illumination
                    state[4] = chr(2)    # Field diaphragm position
                    state[5] = chr(self.aperture)  # Aperture
                    self.__microscope_port.set(A_TEILER,2)  # Enable ICR prism

                    # Set the position of the ICR prism.  This is
                    # magnification dependent.  
                    prism_pos = self.prism_pos[ self.magnification ]
                    self.__microscope_port.set(W_PRISMA,prism_pos)

                elif mode == 'brightfield':
                    # Disable both the ICR and the darkfield unit
                    state[2] = chr(0)    # Brightfield illumination
                    state[4] = chr(2)    # Field diaphragm position
                    state[5] = chr(self.aperture)  # Aperture
                    self.__microscope_port.set(A_TEILER,1) # No ICR prism
                    self.__microscope_port.set(W_PRISMA,0)

                elif mode == 'darkfield':
                    # Disable ICR, enable the darkfield unit.  Enabling
                    # the darkfield mode requires setting the aperture to
                    # 6, which is a special setting for darkfield use, and 
                    # changing the setting of the field diaphragm.
                    state[2] = chr(1)    # Darkfield illumination
                    state[4] = chr(1)    # Field diaphragm position
                    state[5] = chr(6)    # Aperture
                    self.__microscope_port.set(A_TEILER,1) # No ICR prism
                    self.__microscope_port.set(W_PRISMA,0)

                state[0] = chr(11) ; state[1] = chr(6)
                state = string.join(state, "")  # Convert from a list to a string
                self.__microscope_port.ergoplan_send( state )
                self.mode = mode

        # Enable/disable autofocus
        if kw.has_key('autofocus'):
            autofocus = kw['autofocus'].lower()
            assert autofocus in ['on', 'off']
            params_used.append( 'autofocus' )
            if autofocus == 'on':
                self.__microscope_port.enable(SRCH_FOC)
                self.autofocus = True
            else:
                self.__microscope_port.disable(SRCH_FOC)
                self.autofocus = False
                        
        # The STATUS command (p65) is used to enquire whether all the
        # stage's motors have ceased moving.  It returns 'N' if no
        # motors are running, and 'B' if one or more motors are still
        # active.
        t2 = time.time()
        if 0: # XXX self.config.ins1000.wait_after_move:
            while 1:
                resp = self.__stage_port.send_cmd('status')
                if string.lower(resp[0]) == 'n':
                    break

        t3 = time.time()
        if TIMING:
            print '*** waiting time in move:', t3 - t2

        # Subtract the time spent waiting in the above loop from the
        # requested delay
        delay = delay - ( t3 - t2 )
        if delay>0:
            time.sleep(delay)
            
        # Update the current values of the scope's position
        self.read_hardware_status()
        if TIMING:
            now = time.time()
            print '*** read_hardware_status time:', now - t3
            print '*** Low-level move time:', now - start_cmd

        return params_used

    
    def read_autofocus_pos(self):
        """Wait for the autofocus to settle down, and read the final
        autofocus position."""
        
        config = get_configuration()
        
        # This function is not currently used at the moment, because
        # it seems to really, really slow down the autofocus process.
        # Instead, z_autofocus is assumed to be the same as z_pos
        # whenever self.autofocus is true (the autofocus is turned on)        
        msg = chr(READ_LFS) + chr(FOCUS) + 11*chr(0)
        last = None
        while 1:
            resp = self.__microscope_port.ergoplan_send( msg )
            if resp == last:
                break
            last = resp
            # Pause for a quarter of a second
            select.select([], [], [], .25)
            
        self.z_autofocus = self.__microscope_port.get(Z_TRIEB)
        if config.get_debug():
            print 'Autofocus position set to', self.z_autofocus

        # Compute the upper and lower limits of safe Z coordinates.
        # The lower limit is always zero, because it's always safe to
        # move the stage down.  The upper limit is derived this way:
        # the 100x lens has a working distance of .3mm = 300 microns.
        # We'll give the user 50 microns of freedom, which is
        # 50/.018 = 2777 units.
        self.z_min = 0
        self.z_max = self.z_autofocus + 2777
        
    def scope_cmd(self, cmd):
        "Send a command straight through to the scope."
        return self.__stage_port.send_cmd( cmd )

    def close(self):
        "Put the microscope to bed when shutting down"
        if self.__stage_port is not None:
            self.__stage_port.close()
        if self.__microscope_port is not None:
            self.set(light = 0)        # Douse the light when shutting down
            self.__microscope_port.close()

        self.__stage_port = None
        self.__microscope_port = None
        
