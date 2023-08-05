#
# Distributed under the terms described in the LICENCE file.
#

"""mems.instrument.server.configuration

Class for storing the configuration of the microscope server.

"""

__revision__ = "$Id: configuration.py,v 1.16 2003/01/02 16:19:38 akuchlin Exp $"

import os, socket
import ConfigParser

# List of (section, option) values which are integers
INT_VALUES = [('server', 'port'),
              ('server', 'http-port'),
              ('server', 'dim-light-seconds'),
              ('server', 'dim-light-percentage'),
              ('server', 'num-frames'),
             ]

BOOLEAN_VALUES = [('server', 'allow-control'),
                  ('server', 'center-stage'),
                  ('server', 'rotate-stage'),
                  ]

class Section:
    def __init__ (self, name):
        self.name = name

class Configuration:
    """
    The Configuration class parses a configuration file, and returns an
    object with an attribute for each section of the config file; each
    Section is an object bristling with attributes, one for every option
    in that section.

    For example:
    config            (The Configuration instance)
    config.server     (The [server] section of the configuration)
    """


    def __init__ (self, options):
        """Configuration(options:Options)
        """

        if options is None:
            from mems.instrument.server.options import Options
            options = Options([])
        self.options = options

    def read (self, filename):
        """Configuration(filename: string)

        Open and parse the specified configuration file.
        """
        if not os.path.exists(filename):
            raise IOError, "Configuration file '%s' not found" % filename

        fp = open(filename)
        self.readfp(fp, filename)

    def readfp (self, fp, filename=None):
        parser = ConfigParser.ConfigParser()
        parser.readfp(fp, filename)

        for name in parser.sections():
            orig_name = name ; name = name.lower()
            name_attr = name.replace('-', '_')
            sect = Section(name)
            setattr(self, name_attr, sect)
            for opt in parser.options(orig_name):
                opt = opt.lower()
                opt_attr = opt.replace('-', '_')

                if (name, opt) in INT_VALUES:
                    value = parser.getint(orig_name, opt)
                elif (name, opt) in BOOLEAN_VALUES:
                    value = parser.getboolean(orig_name, opt)
                else:
                    value = parser.get(orig_name, opt)

                setattr(sect, opt_attr, value)

    def get_root_dir (self):
        """get_root_dir() -> string
        Return the root directory where temporary files can be written.

        """
        if not hasattr(self, 'server') or not hasattr(self.server, 'root_dir'):
            # Default location
            return '/www/var/microscope/'

        return self.server.root_dir

    def get_num_frames (self):
        """get_num_frames() -> number
        Return the number of frames per second to send.

        """
        if not hasattr(self, 'server') or not hasattr(self.server,
                                                      'num_frames'):
            # Default number of frames -- 2/second seems a reasonable
            # compromise between the fast frame grabbers and the slow
            # DMCs.
            return 2

        return self.server.num_frames

    def get_debug (self):
        """get_debug() -> boolean
        Return whether the debugging is on/off.
        """
        if self.options.debug: return 1
        return 0

    def get_error_email (self):
        """get_error_email() -> string
        Returns the e-mail address where tracebacks should be sent, or None
        if they shouldn't be sent anywhere.
        """
        if not hasattr(self.server, 'error_email'):
            return None
        return self.server.error_email

    def mail_error (self, msg, error_summary):
        """Send an email notifying someone of a traceback."""

        error_email = self.get_error_email()
        if error_email is None or self.get_debug():
            return

        cmd = "/usr/lib/sendmail '%s'" % error_email
        pipe = os.popen(cmd, 'w')
        pipe.write('Subject: uscope traceback (%s)\n' % error_summary)
        pipe.write('From: "%s microscope" <%s>\n' % (socket.getfqdn(),
                                                     error_email))
        pipe.write('To: %s\n' % error_email)
        pipe.write('\n')
        pipe.write(msg)
        pipe.close()

    def get_camera_class (self):
        server_cfg = self.server
        devno = 1
        while 1:
            key = 'device%i' % devno
            if not hasattr(server_cfg, key):
                break

            devno += 1
            devname = getattr(server_cfg, key)

            if devname == 'fake_camera':
                from mems.instrument.server.fake_camera import FakeCamera
                return FakeCamera
            elif devname == 'pxc_200':
                from mems.instrument.server.pxc_200 import PXC200Camera
                return PXC200Camera
            elif devname == 'dmc':
                from mems.instrument.server.dmc import DMCCamera
                return DMCCamera

        raise RuntimeError, 'No camera device found'


_config = None
def get_configuration (options=None):
    global _config
    if _config is None:
        _config = Configuration(options)
    return _config
