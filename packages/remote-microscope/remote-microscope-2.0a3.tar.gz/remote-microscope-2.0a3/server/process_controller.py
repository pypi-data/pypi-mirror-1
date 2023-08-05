"""mems.instrument.server.process_controller

The ProcessController class creates a bunch of subprocesses, and
restarts them if they die.

"""

__revision__ = "$Id: process_controller.py,v 1.35 2003/01/02 16:19:38 akuchlin Exp $"

import os, sys, stat, time
import traceback, cStringIO, logging

from mems.instrument.server import util

log = logging.getLogger('server')

def isfifo (path):
    """isfifo(path:string) -> boolean
    Test whether a path is a FIFO.
    """
    try:
        st = os.stat(path)
    except os.error:
        return 0
    return stat.S_ISFIFO(st[stat.ST_MODE])


class ProcessController:

    # Number of restart times to store in the _restart_times list
    NUM_RESTART_TIMES = 10

    # Number of seconds in which the server can start
    # NUM_RESTART_TIMES child processes.  If it tries to start
    # children more frequently than that, the server will be throttled
    # back.
    MAX_RESTART_DURATION = 5

    def __init__ (self, config, debug=0):
        """ProcessController(config:Configuration, debug:boolean)

        'config' represents the server's configuration.
        'debug', if true, causes debugging output to be printed to stdout.

        """
        self.config = config
        self.open_error_log()

        # Figure out list of processes to start
        self.subprocess_list = self.determine_subprocesses(config)

        # The 'children' dictionary will map the subprocess's name to
        # its PID.
        self.children = {}

        # _restart_times stores the creation times of the
        # NUM_RESTART_TIMES most recent child processes, and is used
        # to throttle the restarting of children.  _pause_time, if
        # non-zero, stores the time at which the server can resume
        # trying to start children again.
        self._restart_times = []
        self._pause_time = 0


    # __init__ ()


    def run (self):
        """run() -> None
        Start all the children and monitor them continually.
        The loop can be exited by clearing subprocess_list and killing
        all the children.
        """

        self.make_fifos()
        fifo = util.open_fifo('master')

        if not self.config.get_debug():
            self.daemonize()

        while len(self.subprocess_list):
            for key, child_func in self.subprocess_list:
                if (not self.children.has_key(key) and
                    self.record_start(key) ):
                    self.start_process(key, child_func)

            # Wait for one of the children to exit
            dead_pid, status = os.waitpid(-1, 0)
            log.info("process_controller: Child %i died" % dead_pid)

            # Now we have to figure out which child died, and remove
            # it from self.children
            for key, pid in self.children.items():
                if pid == dead_pid:
                    del self.children[key]

    def make_fifos (self):
        """make_fifos() -> None

        Create FIFOs to be used by subprocesses, first deleting any
        existing FIFOs.
        """

        root_dir = self.config.get_root_dir()
        if not os.path.exists(root_dir):
            os.makedirs(root_dir, mode=0755)

        for name in os.listdir(root_dir):
            path = os.path.join(root_dir, name)
            if isfifo(path):
                try:
                    log.debug("Unlinking FIFO %s" % path)
                    os.unlink(path)
                except os.error:
                    log.error("process_controller: Unable to unlink FIFO %r"
                              % path)
                    raise SystemExit

        # Create one FIFO for each subprocess, plus one for the process
        # controller.
        fifo_names = [key for key, child_func in self.subprocess_list]
        fifo_names.append("master")
        for name in fifo_names:
            util.make_fifo(name)


    def daemonize (self):
        # Fork once
        if os.fork() != 0:
            os._exit(0)
        os.setsid()                     # Create new session
        if os.fork() != 0:
            os._exit(0)
        os.chdir("/")
        os.umask(0)
        sys.stdout = sys.stderr

        os.close(sys.__stdin__.fileno())
        os.close(sys.__stdout__.fileno())
        os.close(sys.__stderr__.fileno())

        os.open('/dev/null', 0)
        os.dup(0)
        os.dup(0)

    def open_error_log (self):
        # Errors are logged by just writing them to sys.stderr.
        # In debugging mode, sys.stderr is left alone so messages
        # will go to the screen; in production mode, though, stderr
        # is redirected to a file.
        if self.config.get_debug():
            logging.basicConfig()
            log.setLevel(logging.DEBUG)
            return

        root_dir = self.config.get_root_dir()
        filename = os.path.join(root_dir, 'microscope.log')
        root_log = logging.FileHandler(filename)


    def record_start (self, process_name):
        """record_start() -> boolean

        Record the starting of a child process.  If the server seems to be
        respawning too quickly, the server will pause.
        """
        now = time.time()
        # If we're pausing, just return without logging anything
        if now < self._pause_time:
            return 0
        self._pause_time = 0

        self._restart_times.append(now)
        self._restart_times = self._restart_times[-self.NUM_RESTART_TIMES:]
        diff = now - self._restart_times[0]
        if (len(self._restart_times) == self.NUM_RESTART_TIMES and
            diff < self.MAX_RESTART_DURATION):
            # We've restarted NUM_RESTART_TIMES times in the last
            # MAX_RESTART_DURATION seconds, so something is probably
            # wrong.
            log.error("process_controller: Respawning process %r too fast; pausing for 30 seconds"
                      % process_name)
            self._pause_time = now + 30
            return 0
        else:
            return 1


    def start_process (self, key, child_func):
        """start_process(key:string, child_func:function) -> int
        Start a new subprocess and execute the requested function
        """
        pid = os.fork()
        if pid != 0:
            # We're the parent
            self.children[key] = pid
            log.info("process_controller: Starting %s with pid %i" % (key, pid))
            return pid

        # Prepare to start the child's main function.  First import
        # the module and get the function.  child_func starts out as a
        # string containing something like
        # 'mems.instrument.server.fake_camera.main'.  We assume the
        # last component is the function name, import the module, and
        # then traverse the modules to get the function.  The module
        # name comes from Python code that makes up the microscope
        # server, so security is not an issue here.

        components = child_func.split('.')
        mod_name = '.'.join(components[:-1])
        child_func = __import__(mod_name)
        for c in components[1:]:
            child_func = getattr(child_func, c)

        # Open this process's FIFO and set it as stdin.
        sys.stdin = util.open_fifo(key)
        sys.stdout = sys.stderr

        # We're the child, so call the function and exit immediately,
        # catching any tracebacks.
        # XXX catch and log/mail tracebacks here!
        try:
            child_func()
        except KeyboardInterrupt:
            pass
        except:
            error_file = cStringIO.StringIO()
            (exc_type, exc_value, tb) = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, tb,
                                      file=error_file)


            error_email = self.config.get_error_email()

            log.critical('%s, pid %i: Died with exception:\n%s' %
                         (key, os.getpid(), error_file.getvalue()))
            # XXX at some point we might want to use the e-mail
            # support provided by the 'logging' package.
            self.config.mail_error(error_file.getvalue(),
                                   repr(exc_value))
        os._exit(0)


    def determine_subprocesses (self, config):
        """determine_subprocesses(config:Configuration) -> [(string,function)]

        Figures out which subprocesses need to be executed by
        examines the specified configuration 'config'.
        Returns a list of (process name, function) tuples.
        """

        L = []
        L.append( ('network_server',
                   'mems.instrument.server.network_server.main') )
        server_cfg = config.server
        devno = 1
        while 1:
            key = 'device%i' % devno
            if not hasattr(server_cfg, key):
                break

            devno += 1
            devname = getattr(server_cfg, key)
            if devname in ['fake_camera', 'dmc', 'pxc_200']:
                pass
            elif devname == 'fake_microscope':
                if server_cfg.allow_control:
                    L.append(('microscope',
                              'mems.instrument.server.fake_microscope.main'))
            elif devname == 'inm200':
                if server_cfg.allow_control:
                    L.append(('microscope',
                              'mems.instrument.server.inm200.main'))
            elif devname == 'ins1000':
                if server_cfg.allow_control:
                    L.append(('microscope',
                              'mems.instrument.server.ins1000.main'))
            else:
                # XXX should report an error more neatly
                raise ValueError, 'Unknown device: %r' % devname


        return L


# class ProcessController

