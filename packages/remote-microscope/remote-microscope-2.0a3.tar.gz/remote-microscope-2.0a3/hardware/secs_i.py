# secs_i.py : Partial implementation of the SECS-I standard
#
# Distributed under the terms described in the LICENCE file.
#
# Partial implementation of the SECS-I (SEMI Equipment Communications
# Standard) Protocol : SEMI E4-0298
#
# References in brackets like [1.2] are to the SECS-I specification.
#
# Handling of single-block messages works; the code for messages that
# would be broken up into multiple blocks is included here, but it's
# never been tested, because the microscope controller never sends or
# receives such large messages.
#
# This will probably be difficult to understand unless you know about
# the SECS-I protocol; it's recommended that you read the protocol
# specification before diving into this code.  The protocol spec is
# only about 20 pages or so, and it's not terribly complicated.
# You can download a copy for $50 from www.semi.org; please don't ask me
# to send you a copy, because I can't.
#
# To use this, create a SECS_I class, and add a .fd attribute containing
# an integer giving the file descriptor to use for communicating via
# SECS-I; this will usually have been some serial device like /dev/ttyS0.
# Use .send_message(msg) to send a message,
# .receive_message() to read incoming messages and add them to an
# internal queue, and get_message() to pull a message off the queue.

__revision__ = "$Id: secs_i.py,v 1.4 2002/05/02 15:07:48 akuchlin Exp $"

Error = "SECS-I protocol error"

import struct, select, os, time

# This doesn't use the Options class for its debugging setting, because
# you'll rarely be concerned with debugging at the low level of the SECS-I
# protocol.
DEBUG = 0
_timing = 0

# Handshake bytes [5.2] used to arbitrate which side gets to send data
# when initiating a transmission.

ENQ = chr(5)                            # Request to send
EOT = chr(4)                            # Ready to receive
ACK = chr(6)                            # Correct reception
NAK = chr(21)                           # Incorrect reception

class SECS_I:
    # Default values for the various timeout and retry parameters;
    # these are the typical values cited in [8.1].
    T1 = 0.5                            # Inter-character timeout
    T2 = 10                             # Protocol timeout
    T3 = 45                             # Reply timeout
    T4 = 45                             # Inter-block timeout
    RTY = 3                             # Number of times to retry
    
    def __init__(self):
        """Create SECS-I object.  It's assumed that a .fd attribute will 
        be added, containing a file descriptor."""
        self.blocks_to_send = []
        self.block_queue = []
        self.message_queue = []  # Queue of completely received messages
        self.__received = {}     # Used for assembling multi-block messages
	self.__system_bytes = 1  # Used when automatically generating
                                 # system bytes
        
    def write(self, string):
        "Write a string to the descriptor"
	if DEBUG: print 'Writing to microscope', repr(string)
	os.write(self.fd, string)

    def __wait_for_char(self, timeout):
        """Wait timeout seconds for a character to arrive over the
        RS-232 connection.  Returns an empty string if no character
        was received before the timeout."""
        if DEBUG: print "Waiting time", timeout, "for char from scope"
        if _timing: now = time.time()
	read, write, dummy = select.select([self.fd], [], [], timeout)
	if len(read)==0: 
	    if DEBUG: print "Read nothing"
	    return ""
	else: 
            data = os.read(self.fd, 1)
	    if DEBUG: print "Read byte:", repr(data)
            if _timing:
                print 'Waited for', time.time() - now, 'out of', timeout,'sec'
            return data
    
    def send_block(self, block):
        """Send a single block over the wire.  The block is a string,
        and must contain the proper SECS-I header."""

        # Check the block's length [5.6]
        if len(block)<10 or len(block)>254:
            raise Error, ("Block length of %i is not between 10 and 254" %
                          (len(block),) )
        
        # Make RTY attempts to send the block [5.4, 5.8.2.2]
        retry = 0
        while retry <self.RTY:
            # Send an ENQ, then wait for the returning byte; if it's EOT,
            # we can send the block.  If it's another ENQ, the master is
            # trying to send, so we have to receive the block [5.8.2]
            self.write( ENQ )
            while 1:
                c = self.__wait_for_char(self.T2)
                if c == "" or c == ENQ or c==EOT:
                    break
                # If we received a character that isn't either ENQ or
                # EOT, we ignore it and simply wait for another
                # character [5.8.2.1]
                pass
            
            if c == "":  # We timed out; try again [5.8.2.2]
                retry = retry + 1
            elif c == ENQ:
                # The master is trying to send, so we have to go call
                # the receive_block() method to read the block it
                # wants to send. [5.8.2.1]
		self.write( EOT )
                self.receive_block()
                retry = 0               # Reset the retry count to zero
                                        
            elif c == EOT:
                # Yay!  We can send our block.  Here's where all the
                # real work gets done.

                # Compute checksum of the length plus the block [5.7]
                csum = 0#len(block)
                for c in block:
                    csum = (csum + ord(c)) & 0xFFFF

                # Send block [5.8.3]
                self.write( chr(len(block)) )
                self.write(block)
                self.write( struct.pack('>H', csum) )

                # Wait for either an ACK or a NAK
                c = self.__wait_for_char( self.T2 )
                if c == ACK:
                    # Yay (again)! The other side has acknowledged the 
                    # block, so we're done. [5.8.3]
		    if DEBUG: print 'ACK received; block successfully sent'
                    return
                else:
                    # Either we timed out while waiting for the ACK,
                    # or the character that was received wasn't ACK.
                    # Therefore we'll just retry sending the block
                    # again [5.8.3]
		    if DEBUG: print 'NAK received; retrying'
                    retry = retry + 1

        raise Error, "Send failed after %i retries" % (self.RTY,)


    def receive_block(self, timeout = None):
        """Receive a block and add it to the list of received blocks."""
	if DEBUG: print 'Receiving a block'
        if timeout is None: timeout = self.T2
        # Wait for timeout seconds for the length byte [5.8.4, 5.8.5]
        length_byte = self.__wait_for_char( timeout )
        if length_byte == "":
            # We timed out waiting, so send a NAK. [5.8.5]
	    if DEBUG: print 'Timed out waiting; sending NAK'
            self.write( NAK )
            return

        length = ord(length_byte)
        if length<10 or length>254:
            # Invalid length; read and discard the rest of the
            # characters, and then send a NAK. [5.8.5]
	    if DEBUG: print 'Invalid length', length
            self.__discard_chars()
            self.write( NAK )
            return
        
        csum = 0
        block = ""
        # Loop getting characters until we've either gotten them all,
        # or timed out. [5.8.5]
        while (len(block) < length+2):
            c = self.__wait_for_char( self.T2 )
            if c == "":
                # We timed out waiting, so send a NAK. [5.8.5]
                self.write( NAK )
                return

            if len(block) < length:
                csum = (csum + ord(c)) & 0xFFFF
            block = block + c
	    if DEBUG:
		print 'Partial message (%i/%i): %s %i' % (len(block), length+2,
						       repr(block), csum)

        # We've stuck the two bytes representing the checksum onto the 
        # end of the block; take them off and compare checksums.
        sent_csum = (ord(block[-2])<<8) + ord(block[-1])
        block = block[:-2]

        if sent_csum != csum:
            # Invalid checksum; read and discard the rest of the
            # characters, and then send a NAK. [5.8.5]
	    if DEBUG: 
	        print "Checksum failed: sent=%i computed=%i" %(sent_csum, csum)
            self.__discard_chars()
            self.write( NAK )
            return

        # The block is OK, so we add it to the list of blocks and
        # return an ACK
        self.block_queue.append( block )
        self.write( ACK )
        return                          # ... And we're done.
    
    def __discard_chars(self):
        """Read and discard characters until the other side has finished 
        sending; this occurs when we've waited T1 seconds without any
        activity."""
        while 1:
            c = self.__wait_for_char( self.T1)
            if c == "": return
            

    # Higher-level message sending operations

    def send_message(self, message, reply_needed = 0,
                     device_id=1, message_id=1,
                     system_bytes = None, R=0):

        # XXX should add range checks for all the parameters here

        if system_bytes is None:
            self.__system_bytes = self.__system_bytes+1
            system_bytes = self.__system_bytes

        # The blocks are numbered starting from 1 [6.7]
        block_num = 1

        # Break the whole message up into 244-byte blocks
        last_block, dummy = divmod(len(message), 244)
        last_block = last_block * 244

        for i in range(0, len(message), 244):
            E = (i == last_block)
            block = message[i:i+244]
            
            # Construct the header, as explained in section 6 of the
            # SECS-I docs. 
            header = struct.pack('>HHHI',
                                 (R << 15) + device_id,
                                 (reply_needed << 15) + message_id,
                                 (E << 15) + block_num,
                                 system_bytes)
            block = header + block
	    if DEBUG: print 'Sending block', repr(block)
            self.send_block(block)
            block_num = block_num + 1
            
        # OK; we have now sent the message, and, since we got this far 
        # with no exceptions, it was correctly received.
        # Now, if a reply was requested, we'll have to read it.
        if reply_needed: return self.receive_message()
        else: return None

    def receive_message(self):
        """Receive a SECS-I message, possibly split into multiple
        blocks.  To retrieve the message, call get_message()."""
        message = ""
        last_header = None              # Header of last block accepted 
        expecting_block = 1             # Next block number we should see
        timeout = self.T3
        while 1:
            # There had better be a block waiting for us; otherwise,
            # this will raise an exception.
	    while len(self.block_queue) == 0:
                # Wait for T4 seconds for the next block [7.4.3]
	        byte = self.__wait_for_char( self.T4 ) 
		if byte == ENQ:
	           self.write( EOT )
		   self.receive_block( timeout )
            block = self.block_queue[0]
            self.block_queue.remove(block)
            header, block = block[:10], block[10:]
            s1, s2, s3, system_bytes = struct.unpack('>HHHI', header)

            if last_header is not None and last_header == header:
                # Duplicate block detected, so discard it [7.4.2]
                continue

            last_header = header        # Save header [7.4.2]
            timeout = self.T4           # Change timing interval [7.4.3]

            # Extract the top bits
            R, W, E = s1 >> 15, s2 >> 15, s3 >> 15
            dev_id, msg_id, block_num = s1 & 32767, s2 & 32767, s3 & 32767

            key = (dev_id, msg_id, system_bytes)
            if self.__received.has_key(key):
                # It's an expected block
                expecting_block, message = self.__received[key]

                # Discard an unexpected block 
                if block_num != expecting_block: continue
                message = message + block
                if E:
                    # This is the final block
                    self.message_queue.append( (msg_id,
                                                    system_bytes,
                                                    message) )
                    return
                else:
                    # It's a middle block, so just store the update
                    self.__received[key] =  expecting_num+1, message
            else:
                # It's the start of a new primary block
                if E:
                    # If E is set, this is the only block there is, so we
                    # can add it to the list of received messages
                    self.message_queue.append( (msg_id,
                                                    system_bytes,
                                                    block) )
                    return
                else:
                    # Remember this partial block 
                    self.__received[key] =  1, block

    def get_message(self):
        """Return the next received message waiting in the queue, or
        None if the queue is empty."""
        if len(self.message_queue) == 0: return None

        msg_id, system_bytes, msg = self.message_queue[0]
        self.message_queue = self.message_queue[1:]
        return msg

