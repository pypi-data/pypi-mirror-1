"""mems.instrument.server.state

Object that contains the microscope server's state.

"""

import cPickle, os, socket, sys, threading, time, xmlrpclib
import base64, logging
from cStringIO import StringIO

from mx.DateTime import now
from PIL import Image

from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText

from PIL import Image, ImageDraw

from quixote import get_session_manager

from mems.instrument import protocols
from mems.instrument.server import layout
from mems.instrument.server import util
from mems.instrument.server.configuration import get_configuration

from mems.lib import MODE

# Hostname of the central server to use
if MODE == 'DEVEL':
    CENTRAL_HOSTNAME = "localhost"
else:
    CENTRAL_HOSTNAME = "www.mems-exchange.org"

log = logging.getLogger('server')
xml_log = logging.getLogger('server.xml')

# Filename to use for pickling the microscope's state
SCOPE_STATE_FILENAME = '/www/var/microscope/state.pkl'

def send_mail (address, message):
    cmd = "/usr/lib/sendmail '%s'" % address
    pipe = os.popen(cmd, 'w')
    pipe.write(message)
    pipe.close()

class MicroscopeState:
    """Holds the current state of the microscope display.

    Instance attributes:
      image : Image
        Image to be returned by clients, including any annotations
        such as the crosshair or scale marker.
      unaltered_image : Image
        Original image without annotations, as obtained directly from the
        camera.
      image_size : string
        Size of image to display; one of small, medium, large, or huge.
      scope_state : { string : any }
        Dictionary holding the microscope's current position and state.
      show_crosshair : bool
        If the crosshair should be displayed.
      show_scale : bool
        If the scale indicator should be displayed.
      allowed_users : [string]
        List of user IDs allowed to connect.  If None,
        anyone can connect.
      run_id : integer
        ID of the run currently being displayed.
      step_names : [string]
        List of step names.  Only has a non-None value if a run ID has
        been set. 
      last_activity : float
        Time of last user activity on the server; this is used to
        automatically dim the lights.
    """

    SIZES = {'small': (216, 162),
             'medium':(320, 240),
             'large': (640, 480),
             'huge':  (800, 600)
             }

    def __init__ (self, camera):
        # Initialize attributes
        self.args = {}
        self.image = None
        self.unaltered_image = None
        self.scope_state = {'x_scale':1.0, 'y_scale':1.0}
        self.show_crosshair = False
        self.show_scale = False
        self.image_size = 'large'
        self.allowed_users = None
        self.run_id = None
        self.step_names = None
        self.camera = camera

    _save_lock = threading.Lock()
    def _save_state (self):
        dict = {
            'allowed_users': self.allowed_users,
            'image_size': self.image_size,
            'run_id' : self.run_id,
            'step_names' : self.step_names,
            'show_crosshair' : self.show_crosshair,
            'show_scale' : self.show_scale,
            }

        pkl = cPickle.dumps(dict)

        self._save_lock.acquire()
        try:
            f = open(SCOPE_STATE_FILENAME, 'w')
            f.write(pkl)
            f.close()
        finally:
            self._save_lock.release()

    def load (self):
        try:
            input = open(SCOPE_STATE_FILENAME, 'r')
        except IOError:
            return
        else:
            dict = cPickle.load(input)
            input.close()
            self.__dict__.update(dict)

        # Update the image size, so that the camera matches the selected state
        self.set_image_size(self.image_size)

    def set_allowed_users (self, allowed_users):
        self.allowed_users = allowed_users
        self._save_state()

    def set_step_names (self, step_list):
        self.step_names = step_list

    def set_run_id (self, user_id, run_id):
        """Retrieve the state for run # 'run_id', as requested by the
        user 'user_id'.  
        """

        self.run_id = run_id
        self._save_state()
        if self.run_id is None:
            self.allowed_users = None
            self.step_names = None
        else:
            self._get_run_info(user_id, run_id)

    def _get_run_info (self, user_id, run_id):
        """Run a subthread to get the list of allowed users and
        other information about the run 'run_id'."""

        def fetch_users ():
            config = get_configuration()
            server = xmlrpclib.Server('http://%s/xml/rpc'
                                      % CENTRAL_HOSTNAME)
            userlist = self._xmlrpc_query(server.list_users_for_run,
                            (config.server.id, user_id, self.run_id))

            xml_log.debug('userlist result for %r: %r' %(user_id, userlist))
            if not userlist:
                # Empty userlist; assume the run doesn't exist,
                # access was denied, or there was an error
                # connecting to the central server.
                self.set_allowed_users(None)
                self.set_step_names(None)
                self.run_id = None
                return

            userlist.sort()
            self.set_allowed_users(userlist)

            steplist = self._xmlrpc_query(server.list_steps_for_run,
                             (config.server.id, user_id,
                              self.run_id))
            xml_log.debug('Step list result %r' % (steplist))
            if steplist is None:
                return

            self.set_step_names(steplist)

        config = get_configuration()
        t = threading.Thread(target=fetch_users)
        t.start()

    def _xmlrpc_query (self, method, args):
        try:
            result = method(*args)
        except xmlrpclib.Fault, exc:
            msg = ('XML-RPC error %r for args %r' % (exc, args))
            self.remember_detailed_error(msg)
            xml_log.error('%s: %s' % (__name__, msg),
                          exc_info=True)
            return
        else:
            return result

    def remember_detailed_error (self, detailed_msg):
        """remember_detailed_error(detailed_msg : string)
        Record a detailed error message that will be returned to
        administrators.
        """
        for sess in get_session_manager().values():
            if 'manage-scope' in sess.privileges:
                sess.add_error_message(detailed_msg)

    def get_focus_increment (self):
        """get_focus_increment() : float
        Return the minimum increment for changing the focus.
        """
        # XXX calculate this depending on the magnification
        return 5.0

    def get_image (self):
        image = self.camera.grab_snapshot()
        w, h = self.SIZES[self.image_size]
        self.unaltered_image = image.resize((w,h))
        self.image = self.unaltered_image.copy()
        self.annotate_image()
        return self.image

    def get_image_width (self):
        w, h = self.SIZES[self.image_size]
        return w

    def get_image_height (self):
        w, h = self.SIZES[self.image_size]
        return h

    def get_image_size (self):
        return self.SIZES[self.image_size]

    def set_image_size (self, size):
        self.image_size = size
        self._save_state()

    def load_image (self, path):
        self.unaltered_image = Image.open(path)
        self.image = self.unaltered_image.copy()
        self.annotate_image()


    def save_image (self, user_id, step_index):
        image = self.camera.grab_hires()
        io = StringIO()
        image.save(io, 'JPEG')
        image = io.getvalue()
        image = base64.encodestring(image)

        # Upload the image to the server
        server = xmlrpclib.Server('http://%s/xml/rpc'
                                  % CENTRAL_HOSTNAME)
        config = get_configuration()
        result = server.attach_file(config.server.id, user_id,
                                    self.run_id, step_index,
                                    image, "Microscope image")

    def request_email (self, addresses, subject):
        if addresses is None:
            return
        if not subject:
            subject = "Microscope image"

        image = self.camera.grab_hires()

        L = self.scope_state.items() ; L.sort()
        L = ['%s=%s' % (k,v) for k,v in L]

        # Generate a MIME message
        for addr in addresses.split():
            msg = MIMEBase('multipart', 'mixed')
            msg['Subject'] = subject + '\n'
            msg['From'] = ('%s server '
                           '<microscope-feedback@mems-exchange.org>\n'
                           % socket.getfqdn() )
            msg['To'] = addr
            msg.preamble = 'This is a MIME-encoded message\n'
            msg.epilogue = ''

            comments = """Remote microscope image.
Time: %s
Image parameters: %s
""" % (now(), ', '.join(L))

            text = MIMEText(comments)
            msg.attach(text)

            # Attach the image
            io = StringIO()
            image.save(io, 'JPEG')
            img = MIMEImage(io.getvalue())
            msg.attach(img)
            img['Content-type'] = 'image/jpeg'

            # Send the message
            send_mail(addr, msg.as_string(unixfrom=0) )


    def set_scope_state (self, args):
        self.scope_state = args

    def move (self, x=None, y=None, z=None,
              magnification=None, mode=None,
              light=None, aperture=None, angle=None,
              autofocus=None):
        args = self.args
        if x is not None: args['x'] = x
        if y is not None: args['y'] = y
        if z is not None: args['z'] = z
        if magnification is not None:
            args['magnification'] = magnification

        if mode is not None:
            args['mode'] = mode

        if aperture is not None:
            args['aperture'] = aperture

        if light is not None:
            args['light'] = light

        if angle is not None:
            args['angle'] = angle

        if autofocus is not None:
            args['autofocus'] = autofocus

    def execute (self, wait=True):
        msg = protocols.build_message_line('move', **self.args)
        util.send_message('microscope', msg)
        self.args.clear()

        if wait:
            # Wait until there's a command available on the input FIFO,
            # up to a maximum of 5 seconds.
            s = time.time()
            util.has_input_waiting(sys.stdin, timeout=5.0)
            e = time.time()
            #print 'Waited', e-s, 'sec'


    def annotate_image (self):
        if self.scope_state is None or self.image is None:
            return
        if self.show_crosshair:
            self._annotate_crosshair()
        if True: # XXX layout
            self._annotate_layout()
        if self.show_scale:
            self._annotate_scale()

    def _annotate_crosshair (self):
        w, h = self.image.size
        cx, cy = w/2, h/2
        img = self.image
        def flip (x, y):
            r,g,b = img.getpixel((x,y))
            flipped = (r ^ 0xff, g ^ 0xff , b ^ 0xff)
            img.putpixel((x,y), flipped)
        for x in range(cx-15,cx+15):
            flip(x, cy)
        for y in range(cy-15,cy+15):
            flip(cx,y)

    def get_pixels (self, microns):
        view_width = self.scope_state['x_scale'] # in microns
        image_width = self.image.size[0]         # in pixels
        return int(microns * image_width / view_width)

    def get_scale_bar_dims (self):
        bar_max = self.image.size[0] / 2
        for microns in (10000, 5000, 2500, 1000, 500, 250,
                        100, 50, 25, 10, 5, 2.5, 1, 0.5, 0.25):
            pixels = self.get_pixels(microns)
            if pixels < bar_max:
                return microns, pixels

    def _annotate_scale (self):
        "Draw a scale bar on the bottom of the image"
        WHITE_BAR_HEIGHT = 35

        im_width, orig_height = self.image.size # pixels
        im_height = orig_height + WHITE_BAR_HEIGHT
        bar_microns, bar_pixels = self.get_scale_bar_dims()

        new_im = Image.new(self.image.mode,
                           (im_width, im_height))
        new_im.paste(self.image, (0,0))

        # Draw the scale
        draw = ImageDraw.Draw(new_im)
        draw.rectangle((0, orig_height, im_width, im_height),
                       fill=(255, 255, 255))

        offset = int(im_width - bar_pixels) / 2
        # (sx, sy) is upper left corner of scale background rectangle
        sx = 2
        sy = orig_height + 1
        msg = str(bar_microns) +' um'

        # Black bar indicating the chosen length
        draw.rectangle((sx + offset, sy + 17,
                        sx + offset + bar_pixels, sy + WHITE_BAR_HEIGHT - 6),
                       fill=(0,0,0))
        # Text message
        text_w, text_h = draw.textsize(msg)
        draw.text((sx + (im_width - text_w) / 2, sy), msg,
                  fill=(128, 128, 128))
        self.image = new_im

    def _annotate_layout (self):
        layout.draw_layout(self, self.image, 'demo.cif')




