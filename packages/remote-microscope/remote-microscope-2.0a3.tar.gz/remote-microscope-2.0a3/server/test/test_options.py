#!/www/python/bin/python

#
# Test script for Options class.
#

__revision__ = "$Id: test_options.py,v 1.4 2002/10/09 11:53:26 akuchlin Exp $"

from sancho.unittest import TestScenario, parse_args, run_scenarios
from mems.instrument.server.options import Options

tested_modules = [ "mems.instrument.server.options" ]

class OptionsTest (TestScenario):

    def setup (self):
        self.opts = Options(['-f', './microscope.cfg', '-v'])

    def shutdown (self):
        del self.opts


    def check_options (self):
        "Option values"
        self.test_true('self.opts.verbose')
        self.test_false('self.opts.center_stage')
        self.test_val('self.opts.config_file', './microscope.cfg')
        
# class OptionsTest


if __name__ == "__main__":
    (scenarios, options) = parse_args()
    run_scenarios(scenarios, options)
