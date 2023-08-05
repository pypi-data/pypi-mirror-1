#
# pxc_200.py : Driver for the ImageNation PXC-200 frame grabber, using
#             a Linux driver.
#

__revision__ = "$Id: pxc_200.py,v 1.31 2003/01/02 16:19:38 akuchlin Exp $"

import fcntl, logging, os, struct, sys, tempfile, time
import pxc200

from PIL import Image
from mems.instrument.server.configuration import get_configuration
from mems.instrument.server.camera import Camera

# Starting values of frame grabber parameters
START_BRIGHT = 75
START_CONTRAST = 164
START_HUE = 164
START_SATU = 164
START_SATV = 164

log = logging.getLogger('microscope.camera')

class PXC200Camera(Camera):
    # Attributes

    def __init__(self):
        Camera.__init__(self)

        # Starting values
        self.brightness = START_BRIGHT
        self.contrast = START_CONTRAST
        self.hue = START_HUE
        self.satu = START_SATU
        self.satv = START_SATV
        self.x, self.y = 320, 240
        self.grab_size = (self.x, self.y)

        self._camera_fd = -1
        self.open()

    def snapshot_period (self):
        return 0.1

    def open(self):
        """open()
        Open the camera device.  If it's already open, .close() is
        automatically called first.
        """

        config = get_configuration()
        if self.grab_size == (640,480):
            filename = '/dev/pxc0Hbgr'
        else:
            filename = '/dev/pxc0bgr'

        log.debug('Opening PXC200 device file=%s' % filename)

        old_fd = self._camera_fd
        if old_fd != -1:
            log.debug(' Closing previously open fd: %i' % old_fd)
            self.close()
            time.sleep(3)
        while 1:
            try:
                self._camera_fd = os.open(filename, os.O_RDONLY)
                log.debug('PXC200 fd=%i' % self._camera_fd)
            except os.error, (errno, msg):
                log.debug('PXC-200 open() error (%i): %s' % (errno,msg))
                time.sleep(1)
            else: break


    def do_size (self, x, y):
        """Receive a size hint from the clients.  Select the size made
        available by the camera that best supports the requested image size.
        """
        self.close()
        self.x, self.y = x,y
        if 320 <= x or 240 <= y:
            self.grab_size = (640,480)
        else:
            self.grab_size = (320,240)
        self.open()


    def grab_snapshot (self):
        "Grab a viewing-quality image from the camera"
        image = Image.new('RGB', self.grab_size)

        f = self._camera_fd

        # Set image parameters
        #fcntl.ioctl(f, pxc200.PX_IOCSBRIGHT,
        #            struct.pack('i', self.brightness) )
        #fcntl.ioctl(f, pxc200.PX_IOCSCONTRAST,
        #            struct.pack('i', self.contrast) )
        #fcntl.ioctl(f, pxc200.PX_IOCSHUE,
        #            struct.pack('i', self.hue) )
        #fcntl.ioctl(f, pxc200.PX_IOCSSATU,
        #            struct.pack('i', self.satu) )
        #fcntl.ioctl(f, pxc200.PX_IOCSSATV,
        #            struct.pack('i', self.satv) )

        # Acquire image
        pxc200.snap(f, image.im.id)
        return image.resize((self.x, self.y))

    grab_hires = grab_snapshot

    def set(self, **kw):
        return apply(self._set, (), kw)

    def _set(self, **kw):
        "Set camera parameters to new values"
        params_used = []

        if kw.has_key('brightness'):
            self.brightness = kw['brightness']
            params_used.append( 'brightness' )
        if kw.has_key('contrast'):
            self.contrast = kw['contrast']
            params_used.append( 'contrast' )
        if kw.has_key('hue'):
            self.hue = kw['hue']
            params_used.append( 'hue' )
        if kw.has_key('satu'):
            self.satu = kw['satu']
            params_used.append( 'satu' )
        if kw.has_key('satv'):
            self.satv = kw['satv']
            params_used.append( 'satv' )

        return params_used


    def close(self):
        """close()
        Close down the camera.
        """
        config = get_configuration()
        old_fd = self._camera_fd
        log.debug('Closing PXC-200 fd %i' % old_fd)
        if old_fd != -1:
            os.close(old_fd)
            self._camera_fd = -1
