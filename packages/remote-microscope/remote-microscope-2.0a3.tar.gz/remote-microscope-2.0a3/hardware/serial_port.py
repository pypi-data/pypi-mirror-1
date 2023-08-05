
# SerialPort.py : Basic serial port class
#
# Distributed under the terms described in the LICENCE file.
#
# Classes for opening a simple RS-232 connections.

import os, termios

class SerialPort:
    """Basic serial port class.

    This simply encapsulates a file descriptor for the desired serial port. 
    """

    def __init__(self, dev):
        fd = self.fd = os.open(dev, os.O_RDWR)
	
	# Save the current state of the serial port
	self.original_state = termios.tcgetattr(fd)
        
	# Set connection parameters to 9600 baud, 8N1, two stop bits
	L = termios.tcgetattr(fd)
	iflag, oflag, cflag, lflag, ispeed, ospeed, chars = L
	ispeed = ospeed = termios.B9600
 	cflag = (cflag & ~termios.CSIZE) | termios.CS8 | termios.CSTOPB
	cflag = (cflag | termios.CLOCAL | termios.CREAD) & ~termios.CRTSCTS
	iflag = termios.IGNBRK
	lflag = 0
	oflag = 0
	chars[ termios.VMIN ] = 1
	chars[ termios.VTIME ] = 5
	iflag = iflag & ~(termios.IXON | termios.IXOFF | termios.IXANY)
	cflag = cflag & ~(termios.PARENB | termios.PARODD)
	L = [iflag, oflag, cflag, lflag, ispeed, ospeed, chars]
	termios.tcsetattr(fd, termios.TCSANOW, L)

    def write(self, string):
        "Write a string to the port"
	os.write(self.fd, string)
    def read(self, N=1):
        "Read a string from the port"
	return os.read(self.fd, N)
	
    def close(self):
	"Restore the port to its starting state and close the file descriptor."
	termios.tcsetattr(self.fd, termios.TCSANOW, self.original_state)
        if self.fd is None: return
	os.close( self.fd )
	self.fd = None

