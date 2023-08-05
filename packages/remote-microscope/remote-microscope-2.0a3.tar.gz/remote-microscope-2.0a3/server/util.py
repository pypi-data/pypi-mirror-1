
__revision__ = "$Id: util.py,v 1.28 2003/01/02 16:19:38 akuchlin Exp $"

import time, os, sys
import errno, logging, select

from mems.instrument import protocols
from mems.instrument.server.configuration import get_configuration

log = logging.getLogger('server')

def has_input_waiting (file, timeout=0.05):
    """has_input_waiting(file:file, timeout:float) -> boolean
    
    Returns true if there's some input to be read from the file object.
    """
    rlist, wlist, xlist =  select.select([file], [], [], timeout)
    return len(rlist) != 0


class FIFO:
    def __init__ (self, filename, fd):
        self.filename = filename
        self.fd = fd

    def fileno (self):
        return self.fd

    def readline (self):
        L = ""
        while 1:
            c = os.read(self.fd, 1)
            L += c
            if c == "\n":
                return L

    def write (self, data):
        """write(data:string)
        Write 'data' to the FIFO.
        """
        try:
            os.write(self.fd, data)
        except os.error, (errnum, errmsg):
            # Ignore errors caused when the reader of the FIFO is dead.
            # Errors other than EPIPE or EAGAIN may indicate some new
            # problem I'm not aware of, so they'll be re-raised.
            if errnum != errno.EPIPE and errnum != errno.EAGAIN:
                raise


    def close (self):
        """close()
        Close the FIFO.
        """
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def unlink (self):
        os.unlink(self.filename)


def make_fifo (fifo_name):
    config = get_configuration()
    root_dir = config.get_root_dir()
    path = os.path.join(root_dir, fifo_name)
    log.debug("Creating FIFO %s" % path)

    # XXX What mode to use?
    os.mkfifo(path, 0600)


def open_fifo (fifo_name, mode=os.O_RDWR):
    """open_fifo(fifo_name:string, mode:integer) -> file

    Open a FIFO for reading.  The default mode is read/write, but the
    caller can override the mode if desired.  Three attempts will be
    made to open the FIFO, in case the process on the other end hasn't
    opened it yet.
    """

    config = get_configuration()
    path = os.path.join(config.get_root_dir(), fifo_name)
    for i in (1,2,3):
        try:
            fd = os.open(path, os.O_NONBLOCK | mode)
            return FIFO(path, fd)
        except os.error, (errnum, errmsg):
            if errnum != errno.ENXIO:
                raise
            time.sleep(0.1)

    raise


def send_message(fifo_name, message):
    """send_message(fifo_name:string, message:string)

    Write a message to the specified FIFO.
    """
    message = message.strip() + '\n'

    f = open_fifo(fifo_name, os.O_WRONLY)
    f.write(message)
    f.close()


