"""mems.instrument.camera

Base class containing common camera code.
"""

import os
import sys
import time
import tempfile
from PIL import ImageChops

from mems.instrument.server import util
from mems.instrument.server.configuration import get_configuration
from mems.instrument import protocols

def image_rmsdiff(im1, im2):
    """Calculate the root-mean-square difference between two images.  Assumes
    images are RGB mode."""

    h = ImageChops.difference(im1, im2).histogram()
    sum = 0
    for i in range(256):
       sum += (h[i] + h[i+256] + h[i+512]) * i**2
    return (sum / (float(im1.size[0]) * im1.size[1])) ** 0.5


def image_compare(im1, im2, threshold=8):
    """Return true if images are nearly equal."""
    if image_rmsdiff(im1, im2) < threshold:
        return 1
    else:
        return 0


class Camera:

    DEFAULT_SIZE = (320, 240)

    def __init__ (self):
        self.image_path = tempfile.mktemp(suffix='.jpg') # XXX bad format
        self.enabled = 0
        self.last_image = None
        self.last_snapshot_time = time.time()
        self.image_changed = 1

    def snapshot_period (self):
        """Return the delay between snapshots.  Subclasses should override
        this based on how quickly they can take snapshots."""
        return 2.0 # conservative, subclasses can set it to something higher

    def _send_image (self, image, hires='no'):
        # Write the image data to a temporary file
        path = tempfile.mktemp(suffix='.jpg')
        image.save(path)

        # Atomically move the temporary file to the final filename.
        os.rename(path, self.image_path)

        util.send_message("network_server",
                          "image path=%s hires=%s" % (self.image_path, hires))

    def do_enable (self):
        self.enabled = 1

    def do_disable (self):
        self.enabled = 0

    def do_snapshot (self):
        now = time.time()
        if (now - self.last_snapshot_time) < self.snapshot_period():
            return # don't take snapshots more often than snapshot_period
        self.last_snapshot_time = now

        image = self.grab_snapshot()
        #if self.last_image and image_compare(image, self.last_image):
        #    self.image_changed = 0
        #else:
        #    self.image_changed = 1
        #self.last_image = image

        self._send_image(self.grab_snapshot(), hires='no')

    def do_hires (self):
        self._send_image(self.grab_hires(), hires='yes')

    def do_size (self, x, y):
        """Receive a size hint from the clients.  The size is the
        maximum size requested by the clients.  Note that scaling is
        done on a per-client basis by the network server."""
        pass

    def grab_snapshot (self):
        """Read an image from the camera device and return it."""
        raise NotImplementedError, 'subclass must implement'

    def grab_hires (self):
        """Read a hi resolution image from the camera device and return it."""
        raise NotImplementedError, 'subclass must implement'

    def __del__ (self):
        try:
            os.unlink(self.image_path)
        except OSError:
            pass

