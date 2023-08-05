"""mems.instrument.network_server

Implements the network server that listens for incoming TCP/IP connections.

"""

import os, socket, sys, time
import binascii, asyncore, logging

from quixote import session
from quixote.publish import SessionPublisher
from scgi.scgi_server import ns_reads

from mems.instrument import protocols
from mems.instrument.server import util, state
from mems.instrument.server.configuration import get_configuration
from mems.lib import MODE
from mems.lib.ticket import verify_ticket

__revision__ = "$Id: network_server.py,v 1.50 2003/01/02 16:19:38 akuchlin Exp $"

# The server's secret AES key
secret_key = None
if MODE == 'DEVEL':
    secret_key = '8694f7eeb41490db4a1076684e22f0e0'

log = logging.getLogger('server')

class ErrorLogging:

    """Mix-in class to handle exceptions.  The exception is simply
    re-raised, terminating the asyncore main loop and propagating up
    to the logging code in process_controller.py.
    """

    def handle_error (self):
        t,v,tb = sys.exc_info()
        raise


class FIFOdispatcher (ErrorLogging, asyncore.file_dispatcher):
    def __init__(self, fd, uscope_state):
        asyncore.file_dispatcher.__init__(self, fd)
        self._line = ""
        self.uscope_state = uscope_state

    def writable (self):
        # The FIFO we open in this module is read-only, so this method
        # can always return false.  If it returns true, then the FIFO's
        # file descriptor winds up in the list of writable fd's passed
        # to select(), and select() always returns it as being
        # writable, so we'd end up consuming 100% of the CPU.
        return 0

    def handle_read(self):
        data = self.recv(80)
        self._line += data

        # If the end of a line is reached, perform the command. 
        index = self._line.find('\n')
        if index != -1:
            config = get_configuration()
            cmd, args = protocols.parse_message_line(self._line[:index])
            self._line = self._line[index+1:]

            log.debug('%s: Received command %s %r' % (__name__, cmd, args))

            self.handle_command(cmd, args)

    def handle_command (self, cmd, args):
        if cmd == "image":
            path, hires = args['path'], args.get('hires', 'no')
            if hires == 'no':
                # Regular snapshot image
                self.uscope_state.load_image(path)
            else:
                self.uscope_state.handle_hires_image(path)

        elif cmd == 'scope_state':
            self.uscope_state.set_scope_state(args)

        elif cmd == "quit":
            log.info('%s: Received quit command; exiting' % __name__)
            if os.path.exists(state.SCOPE_STATE_FILENAME):
                os.unlink(state.SCOPE_STATE_FILENAME)
            os._exit(0)

        else:
            raise RuntimeError, ("%s: Unknown FIFO command %r args=%r"
                                 % (__name__, cmd, args))


class MicroscopeSession (session.Session):
    def __init__ (self, request, id):
        session.Session.__init__(self, request, id)
        ticket = request.environ.get('QUERY_STRING', '')
        self.error_messages = []
        self.process_ticket(ticket)

    def process_ticket (self, ticket):
        self.user = None
        self.privileges = []
        if ticket:
            config = get_configuration()
            try:
                self.user, self.privileges = verify_ticket(ticket,
                                                           config.server.id,
                                                           secret_key)
            except ValueError:
                # Ignore query strings that aren't valid tickets
                pass

    def has_info (self):
        return True

    def add_error_message (self, msg):
        """add_error_message(msg:string)

        Add an error message to the list.  They'll be shown to the user
        the next time they pull down a new HTML page.
        """
        self.error_messages.append(msg)

    def __str__ (self):
        if self.user:
            return "session %s (user %s, privs %s)" % (self.id, self.user,
                                                    '/'.join(self.privileges))
        else:
            return "session %s (no user)" % self.id

class MicroscopeServer (asyncore.dispatcher):
    "Class for the socket listening on the SCGI port"
    def __init__ (self, uscope):
        self.ip = '127.0.0.1'
        self.port = 3001
        asyncore.dispatcher.__init__(self)
        self.create_socket (socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.ip, self.port))
        self.listen(1024)

        self.publisher = SessionPublisher('mems.instrument.server.ui',
                      session_mgr = session.SessionManager(MicroscopeSession))
        self.publisher.read_config('/www/scope/conf/microscoped.cfg')
        config = get_configuration()
        if not config.get_debug():
            self.publisher.setup_logs()
        self.publisher.uscope = uscope

    def handle_accept (self):
        conn, addr = self.accept()
        config = get_configuration()
        channel = MicroscopeChannel(conn, self.publisher)

    def handle_read (self):
        pass


class MicroscopeChannel (asyncore.dispatcher):
    "Class for a connection to the SCGI port"

    def __init__ (self, conn, publisher):
        asyncore.dispatcher.__init__(self, conn)
        self.publisher = publisher

    def handle_read (self):
        input = self.socket.makefile('r')
        output = self.socket.makefile("w")

        headers = ns_reads(input)
        items = headers.split("\0")
        items = items[:-1]
        assert len(items) % 2 == 0, "malformed headers"
        env = {}
        for i in range(0, len(items), 2):
            env[items[i]] = items[i+1]
        env['PATH_INFO'] = env['SCRIPT_NAME']
        env['SCRIPT_NAME'] = ""
        self.publisher.publish(input, output, sys.stderr, env)
        output.flush()
        try:
            input.close()
            output.close()
            self.close()
        except IOError, err:
            log.info("%s: IOError while closing connection ignored: %s" %
                     (__name__, err))

    def handle_write (self):
        pass

def main():
    # Read server's secret key.  We check to ensure that the key isn't
    # world- or group-readable or -writable.
    global secret_key
    if secret_key is None:
        key_file = open(os.path.expandvars('$HOME/.microscope-key'), 'rt')
        fs = os.fstat(key_file.fileno())
        if (fs.st_mode & 0x066):
            log.critical("%s: $HOME/.microscope-key file is "
                         "group/world readable or writable; dying" % __name__)
            time.sleep(4)
            sys.exit(1)
        secret_key = key_file.read().strip()
        key_file.close()

    secret_key = binascii.a2b_hex(secret_key)

    # Load the microscope state from disk, if a file exists
    config = get_configuration()
    camera_class = config.get_camera_class()
    camera = camera_class()
    uscope_state = state.MicroscopeState(camera)
    uscope_state.load()
    uscope_state.get_image()

    # Create SCGI server
    disp = MicroscopeServer(uscope_state)

    # Register the FIFO with asyncore's main loop
    fifo_dispatcher = FIFOdispatcher(sys.stdin.fileno(),
                                     uscope_state)

    # Enter the polling loop
    asyncore.loop()
