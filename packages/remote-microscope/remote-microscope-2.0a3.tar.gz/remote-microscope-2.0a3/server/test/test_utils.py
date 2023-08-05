#!/www/python/bin/python

#
# Test script for mems.instrument.server.util
#

__revision__ = "$Id: test_utils.py,v 1.6 2002/09/24 19:08:12 akuchlin Exp $"

import os

from sancho.unittest import TestScenario, parse_args, run_scenarios

tested_modules = [ "mems.instrument.server.util" ]

from mems.instrument.server import util

class FIFOTest (TestScenario):

    def setup (self):
        util.make_fifo('test')
        self.fifo = util.open_fifo("test", os.O_RDWR)
        
    def shutdown (self):
        if hasattr(self, 'fifo'):
            self.fifo.close()
            self.fifo.unlink()
            del self.fifo
        
    def check_fifo (self):
        "Check reading/writing from a FIFO: 4"

        # Initially there should be no input waiting
        self.test_false('util.has_input_waiting(self.fifo)')

        # Write some data to the FIFO
        self.test_stmt('self.fifo.write("line\\n")')
        
        # Now there should be some input
        self.test_true('util.has_input_waiting(self.fifo)')

        self.test_val('self.fifo.readline()', "line\n")

    def check_send_message (self):
        "Check send_message: 2"
        self.test_stmt('util.send_message("test", " test ")')
        self.test_val('self.fifo.readline()', "test\n")
        
# class FIFOTest


if __name__ == "__main__":
    (scenarios, options) = parse_args()
    run_scenarios(scenarios, options)
