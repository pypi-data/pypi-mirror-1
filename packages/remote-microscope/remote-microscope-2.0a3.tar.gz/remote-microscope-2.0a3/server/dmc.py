"""mems.instrument.server.dmc

Driver for the Polaroid DMC camera.
"""

__revision__ = "$Id: dmc.py,v 1.18 2003/01/02 16:19:38 akuchlin Exp $"

import time

from mems.instrument.server.camera import Camera

# Debugging flag to print timing messages
TIMING = 0

class DMCCamera(Camera):
    """Class for controlling the Polaroid DMC.
    """

    MODE_THUMBNAIL = 'Thumbnail'
    MODE_VIEWFINDER = 'Viewfinder'
    MODE_FULL_FRAME = 'Full frame'
    MODE_SUPER_RESOLUTION = 'Super-Resolution'
    VALID_MODES = (MODE_THUMBNAIL,
                   MODE_VIEWFINDER,
                   MODE_FULL_FRAME,
                   MODE_SUPER_RESOLUTION)

    def __init__ (self):
        "Open serial port connections and initialize instance variables."

        Camera.__init__(self)
        self.__camera = None
        self.x, self.y = (320,240)
        self.open()

    def _set_mode (self, mode):
        assert mode in self.VALID_MODES
        self.__camera.imagemode = mode

    def _get_mode (self):
        return self.__camera.imagemode

    def open (self):
        # Open the camera device, and set its parameters to 
        # reasonable values. 
        self.close()
        import sane
        self.__camera = sane.open('dmc:/dev/camera')
        self._set_mode(self.MODE_FULL_FRAME)
        self.__camera.shutterspeed = 100


    def do_size (self, x, y):
        """Receive a size hint from the clients.  Select an appropriate DMC
        mode.
        """
        self.x, self.y = x,y
        if x <= 80 and y <= 60:
            mode = self.MODE_THUMBNAIL
        elif x <= 270 and y <= 201:
            mode = self.MODE_VIEWFINDER
        elif x <= 801 and y <= 600:
            mode = self.MODE_FULL_FRAME
        elif x <= 1599 and y <= 1200:
            mode = self.MODE_SUPER_RESOLUTION
        else:
            print '** unsupported DMC size', (x, y)
            mode = self.MODE_FULL_FRAME
        self._set_mode(mode)


#    def set(self, **kw):
#        params_used = []
#
#        if kw.has_key('ASA'):
#            params_used.append( 'ASA' )
#            value = kw['ASA']
#            self.__camera.asa = value
#            
#        if kw.has_key('shutterspeed'):
#            params_used.append( 'shutterspeed' )
#            value = kw['shutterspeed']
#            self.__camera.shutterspeed = value
#
#        if kw.has_key('white_balance'):
#            params_used.append( 'white_balance' )
#            value = kw['white_balance']
#            self.__camera.whitebalance = value
#            
#        return params_used


    def _grab_image (self):
        "Grab an image from the camera & return it"
        t1 = time.time()
        self.__camera.start()

        t2 = time.time()
        image = self.__camera.snap()

        t3 = time.time()

        if TIMING:
            print "Start, snap: ", t2-t1, t3-t2
            print '*** Low-level get_image time:', t3 - t1

        return image


    def grab_snapshot (self):
        image = self._grab_image()
        return image.resize((self.x, self.y))

    def grab_hires (self):
        "Grab a high-resolution image from the camera & return it"

        # Switch to highest-resolution mode
        old_mode = self._get_mode()
        self._set_mode(self.MODE_FULL_FRAME) # XXX why not Super-Resolution?
        image = self._grab_image()

        # Restore previous image mode
        self._set_mode(old_mode)

        return image


    def close(self):
        "Put the camera to bed when shutting down"
        if self.__camera is not None:
            self.__camera.close()
            self.__camera = None
