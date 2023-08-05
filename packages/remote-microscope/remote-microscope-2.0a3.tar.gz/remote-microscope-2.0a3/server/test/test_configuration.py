#!/www/python/bin/python

#
# Test script for Configuration object
#

__revision__ = "$Id: test_configuration.py,v 1.4 2002/09/24 19:08:12 akuchlin Exp $"

import StringIO
from sancho.unittest import TestScenario, parse_args, run_scenarios
from mems.instrument.server.configuration import Configuration
from mems.instrument.server.options import Options

tested_modules = [ "mems.instrument.server.configuration" ]

class ConfigurationTest (TestScenario):

    def setup (self):
        self.fp = StringIO.StringIO("""[camera]
name: dmc
brightness: yes

[UPPERCASE]
NAME: Caps

[Server]
Port: 19000
HTTP-PORT: 19001
Wait-after-move: 1
""")        
        self.cfg = Configuration(Options([]))
        self.cfg.readfp(self.fp)

    def shutdown (self):
        del self.fp


    def check_string_attrs (self):
        "Check string-valued attributes: 2"
        self.test_val('self.cfg.camera.name', 'dmc')
        self.test_val('self.cfg.uppercase.name', 'Caps')

    def check_int_attrs (self):
        "Check integer-valued attributes: 2"
        self.test_val('self.cfg.server.port', 19000)
        self.test_val('self.cfg.server.http_port', 19001)

    def check_bool_attrs (self):
        "Check boolean-valued attributes: 1"
        self.test_true('self.cfg.server.wait_after_move')

# class ConfigurationTest


if __name__ == "__main__":
    (scenarios, options) = parse_args()
    run_scenarios(scenarios, options)
