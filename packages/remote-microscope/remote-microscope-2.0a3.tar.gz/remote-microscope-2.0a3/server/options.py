#
# Distributed under the terms described in the LICENCE file.
#

"""mems.instrument.server.options

Class containing the command-line options.
"""

__revision__ = "$Id: options.py,v 1.13 2003/01/02 16:19:38 akuchlin Exp $"
__version__ = "2.0a2"

import getopt, os, socket, sys

__doc__ = """
Remote Microscope server: """ + __version__ + """
Usage: server.py [options]
Available options:
   -c, --center         Center the stage when initializing microscope
   -d, --debug          Display debugging trace messages
   -f, --cfg <file>     Use specified configuration file
   -h, --help		Display this help message
   -t, --timing         Display timing trace messages
   -v, --verbose        Display verbose activity messages
"""

class Options:
    def __init__ (self, args):
        """Options(args: [string])
        Parses the command-line arguments for the microscope server.
        'args' will usually be the 
        """

        self.center_stage = 0
        self.debug = 0
        self.timing = 0
        self.verbose = 0
        self.config_file = os.path.join('/www/scope/conf',
                                        socket.getfqdn().lower() + ".cfg")

        # Parse command-line options
        opts, args = getopt.getopt(args,
                                   'cdf:htv',
                                   ['center', 'cfg=', 'debug',
                                    'help',
                                    'timing', 'verbose', ])

        for opt, param in opts:
            if opt == '-h' or opt == '--help':
                print __doc__
                sys.exit(0)
            elif opt == '-c' or opt == '--center':
                self.center_stage = 1
            elif opt == '-d' or opt == '--debug':
                self.debug = 1
            elif opt == '-f' or opt == '--cfg':
                self.config_file = param
            elif opt == '-t' or opt == '--timing':
                self.timing = 1
            elif opt == '-v' or opt == '--verbose':
                self.verbose = 1


