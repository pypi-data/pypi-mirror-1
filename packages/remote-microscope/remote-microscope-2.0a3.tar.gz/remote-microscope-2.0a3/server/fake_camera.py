"""mems.instrument.fake_camera

Implementation of a simulated camera device.
"""

__revision__ = "$Id: fake_camera.py,v 1.22 2003/01/02 16:19:38 akuchlin Exp $"

from PIL import Image
from mems.instrument.server.camera import Camera
from mems.instrument.server import shared_map

# Global variable holding the current image
IMAGE = None

# Read in the microscope image to use in the fake display.  This image
# will be given a margin of 800x600 pixels around it,
image = Image.open('/www/scope/docroot/images/microscope-image.png')
IMAGE = Image.new(image.mode,
                  (image.size[0]+2*800, image.size[1]+2*600))
IMAGE.paste(image, (800,600))


class FakeCamera (Camera):

    def __init__ (self):
        Camera.__init__(self)
        self.image_index = 0
        self.width, self.height = (640, 480)
        shared_map.map_open()

    def snapshot_period (self):
        return 0.1

    def grab_snapshot (self):
        scope = shared_map.read_map()
        # No microscope state yet, so just return a blank image
        if scope is None:
            return Image.new('RGB', self.DEFAULT_SIZE)

        # Find center of master image
        x_size, y_size = IMAGE.size
        xc, yc = x_size / 2, y_size / 2

        # Find center and size of displayed image
        ix, iy = xc - scope.x, yc - scope.y
        scale = float(scope.magnification) / scope.DEFAULT_MAGNIFICATION
        width, height = 320, 240
        width /= scale ; height /= scale

        # Get that rectangle of the master image and return it
        image = IMAGE.crop((ix-width/2, iy-height/2,
                            ix+width/2, iy+height/2) )
        return image.resize((self.width, self.height))

    def grab_hires (self):
        image = Image.open('/www/scope/docroot/images/microscope-image.png')
        return image

    def do_size (self, x, y):
        self.width, self.height = x, y
        
