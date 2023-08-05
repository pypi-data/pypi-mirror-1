"""mems.instrument.protocols

Contains various functions and classes for protocol-related parsing tasks.
This module doesn't deal with TCP/IP or anything like that, just the packet
formats used by the microscope.

"""

import re, string, types

# Pattern matching an argument
argument_pat = re.compile(r"""(?x)
\s* (\w+) \s* = \s*         # command name and '=' sign
(
 "(?: [^"]|\")*?" |         # double quoted string
 '(?: [^']|\')*?' |         # single quoted string
 \S+                        # simple word
)
(?= \s|$)
""", re.VERBOSE)

def findall(pattern, source):
    """findall(source) -> list

    Return a list of all non-overlapping matches of the compiled
    pattern in string. If one or more groups are present in the
    pattern, return a list of groups; this will be a list of
    tuples if the pattern has more than one group. Empty matches
    are included in the result.

    """
    pos = 0
    end = len(source)
    results = []
    append = results.append
#    print source
    while pos <= end:
        m = pattern.search(source, pos, end)
#        print 'match', m
        if not m:
            break
        i, j = m.span(0)
        gr = []
#        print m.span(1), m.span(2)
        for (a, b) in [m.span(1), m.span(2)]:
#            print a,b
            gr.append(source[a:b])
        gr = tuple(gr)
        append(gr)
        pos = max(j, pos+1)
#    print 'results', results
    return results


def parse_arguments (line):
    """parse_arguments(line:string) -> dict
    Parse a line containing name/value pairs, and return the resulting
    dictionary of parameters.
    """
    matches = findall(argument_pat, line)
    args = {}
    for name, value in matches:
        if value[0] == value[-1] and value[0] in '\'"':
            value = value[1:-1]
	    value = string.replace(value, "\\'", "'")
	    value = string.replace(value, '\\"', '"')
        else:
            # Try converting the value to an integer.  Quoted
            # values will not be converted.
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
        args[string.lower(name)] = value
    return args


def parse_message_line (line):
    """parse_message_line(line:string) -> (string, dict)
    Parse a line containing a message in the microscope's control
    protocol, and return the command name and argument dictionary.

    Example: the following line
    CHATDISPLAY user=amk message="What's wrong with the wafer?"
    will return
    ('chatdisplay', {'user':'amk', ...})
    """
    line = string.strip(line)
    if line == "":
        raise ValueError, "Blank line received as message"

    # Get the command name
    L = string.split(line, None, 1)
    L[0] = string.lower(L[0])                 # Lowercase the command
    if len(L) == 1:
        # No arguments
        return (L[0], {})

    return (L[0], parse_arguments(L[1]))


def build_message_line (cmd, **kwargs):
    """build_message_line(cmd:string, **kwargs) -> string

    Build a message line, ensuring that the resulting line of text is
    well-formed.  Newlines and tabs are converted to spaces;
    strings are properly quoted.
    """
    msg = string.strip(cmd) + ' '
    for key, value in kwargs.items():
        if (isinstance(value, types.IntType) or
            isinstance(value, types.LongType) or
            isinstance(value, types.FloatType)):
            value = str(value)
        else:
            # Assume it's a string
            value = str(value)

            # Replace newlines, tabs, and quotes
            value = string.replace(value, '\n', ' ')
            value = string.replace(value, '\t', ' ')
            
            if '"' not in value:
                value = '"' + value + '"'
            elif "'" not in value:
                value = "'" + value + "'"
            else:
                # Both quote marks are present, so use double
                # quotes and escape them in the string
                value = string.replace(value, '"', '\\"')
                value = '"' + value + '"'
                                    
        msg = msg + "%s=%s " % (key, value)
    return string.strip(msg) + '\n'

    
#
# A second packet format is used for bits of the actual microscope
# image.  This format is as follows: 
#    size of packet in ASCII characters, followed by an ASCII 0 byte.
#    a codec name, followed by an ASCII 0 byte.
#    a possibly-empty line of arguments, followed by an ASCII 0 byte.
#    raw data
#
# After the first two null-terminated strings,  the rest of the packet
# is raw data, to be interpreted by the selected codec as it sees fit.
#
# For example, one codec might be called "tile".  Its arguments might
# contain the X,Y size of the entire image, and the size of a tile
# within that larger image.  The raw data could then be the image
# data for that title, expressed as a JPEG.  Codec names and argument names
# are case-insensitive, and will be folded to lowercase.
#

def make_packet (codec_name, data, **args):
    """make_packet(codec_name:string, args:dict, data:string)
    Assemble a packet from its components.
    """

    codec_name = string.lower(string.strip(codec_name))
    # Turn arguments into a line
    # XXX doesn't do quoting, values with spaces,
    kw = ""
    for k, v in args.items():
        kw = kw + '%s=%s ' % (string.lower(k), v)
    kw = string.strip(kw)
    
    assert '\0' not in codec_name
    assert '\0' not in kw
    
    packet = (codec_name + '\0' +
              kw + '\0' +
              data)
    return str(len(packet)) + '\0' + packet


def parse_packet (packet):
    """parse_packet(packet:string) -> (string, string, dict)
    Disassemble a packet, returning the codec name, argument dictionary,
    and the raw data part of the packet.
    """
    
    index = string.find(packet, '\0')
    assert index != -1
    length = int(string.strip(packet[:index]))
    assert length + index + 1 == len(packet), "Packet length doesn't match"
    
    index2 = string.find(packet, '\0', index+1)
    assert index2 != -1
    codec_name = string.lower(string.strip(packet[index+1:index2]))

    # Parse the arguments
    index3 = string.find(packet, '\0', index2+1)
    assert index3 != -1
    args = parse_arguments(packet[index2+1:index3])
        
    data = packet[index3+1:]

    return codec_name, data, args

def read_packet (file):
    """read_packet(file) -> (string, string, dict)
    Read one packet from the given socket-like object,
    and disassemble a packet, returning the codec name, argument dictionary,
    and the raw data part of the packet.
    """

    # Read the size, which is ASCII characters terminated by a null byte.
    s = ""
    while 1:
        c = file.recv(1)
        if c == "\0": break
        s = s + c
    size = int(string.strip(s))

    packet = str(size) + '\0'
    while size > 0:
        chunk = file.recv(size)
        packet = packet + chunk
        size = size - len(chunk)

    return parse_packet(packet)

#
# Constants
#

# Different viewing modes
MODE_BRIGHTFIELD = 'brightfield'
MODE_DARKFIELD = 'darkfield'
MODE_ICR = 'icr'

# Different onscreen annotations for the image
ANNOTATE_NONE = 'none'
ANNOTATE_MEASUREMENT = 'measurement'
ANNOTATE_RECTANGLE = 'rectangle'
