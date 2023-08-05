#!/www/python/bin/python

#
# Test script for mems.instrument.protocol.
#

__revision__ = "$Id: test_protocols.py,v 1.8 2002/01/29 21:56:32 akuchlin Exp $"

from sancho.unittest import TestScenario, parse_args, run_scenarios
from mems.instrument import protocols

tested_modules = [ "mems.instrument.protocols" ]

class ProtocolsTest (TestScenario):

    def setup (self):
        pass
    
    def shutdown (self):
        pass


    def check_arguments (self):
        "Parsing of name/value arguments: 6"
        self.test_val('protocols.parse_arguments("")', {})
        self.test_val('protocols.parse_arguments("cmd foo=bar  plan=9")',
                      {'foo':'bar', 'plan':9})

        self.test_val('protocols.parse_arguments("cmd s=\\"10\\" float=1.0 plan=9")',
                      {'s':'10', 'plan':9, 'float':1.0})

        # Single and double-quoted strings
        self.test_val('protocols.parse_arguments("cmd foo=\\"quoted string\\"  plan=9")',
                      {'foo':'quoted string', 'plan':9})
        self.test_val('protocols.parse_arguments("cmd foo=\'quoted string\' plan=9")',
                      {'foo':'quoted string', 'plan':9})
    
	# Escaped quotation marks
	args = r"foo='don\'t'"
        self.test_val('protocols.parse_arguments(%r)' % args,
                      {'foo':"don't"})


    def check_build_message (self):
        "Check assembly of message lines: 5"
        self.test_val('protocols.build_message_line("cmd")',
                      'cmd\n')
        self.test_val("""protocols.build_message_line("cmd",
                                                      value='a\\'bc')""",
                      'cmd value="a\'bc"\n')

        self.test_val("""protocols.build_message_line("cmd",
                                                      value='a\\n\\tb')""",
                      'cmd value="a  b"\n')

        # Value containing a double quote
        self.test_val('protocols.build_message_line("cmd", value=\'a"b\')',
                      'cmd value=\'a"b\'\n')

        # Value containing both quotation marks
        self.test_val("""protocols.build_message_line("cmd",
                                                      value='a\\\'"b')""",
                      """cmd value="a'\\\"b"\n""")

         
    def check_message_parse (self):
        "Check parsing of messages for the control protocol: 3"
        self.test_val('protocols.parse_message_line("cmd")',
                      ('cmd', {}) )
        self.test_val('protocols.parse_message_line("cmd arg=value")',
                      ('cmd', {'arg':'value'}) )

        # Test a value contained an escaped quote mark
        line = protocols.build_message_line("cmd", value='a\'"b')
        self.test_val('protocols.parse_message_line(line)',
                      ('cmd', {'value':'a\'"b'}) )

    def check_make_packet (self):
        "Check assembly of image packets: 2"
        self.test_val("protocols.make_packet('tile', 'raw')",
                      "9\0tile\0\0raw")
        self.test_val("protocols.make_packet('tile', 'raw', plan=9)",
                      "15\0tile\0plan=9\0raw")
        
    def check_parse_packet (self):
        "Check disassembly of image packets: 2"
        self.test_val("protocols.parse_packet('9\\0tile\\0\\0raw')",
                      ('tile', 'raw', {}) )
        self.test_val("protocols.parse_packet('15\\0tile\\0plan=9\\0raw')",
                      ('tile', 'raw', {'plan':9}) )

    def check_read_packet (self):
        "Check reading of packets: 1"
        import StringIO

        class socketStringIO(StringIO.StringIO):
            def recv(self, length=1):
                return self.read(length)
            
        file = socketStringIO('15\0tile\0plan=9\0raw')
        self.test_val("protocols.read_packet(file)",
                      ('tile', 'raw', {'plan':9}) )
        
# class ProtocolsTest


if __name__ == "__main__":
    (scenarios, options) = parse_args()
    run_scenarios(scenarios, options)
