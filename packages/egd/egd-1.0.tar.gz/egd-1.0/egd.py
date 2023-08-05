#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
""" An interface to an EGD (entropy gathering daemon) random number source.

Programatically call the get_random_bytes() function.
Or as a command line utility, use the "--help" option.

For more information about EGD see:
 * http://egd.sourceforge.net/
 * http://prngd.sourceforge.net/

"""
__author__ = "Deron Meranda <http://deron.meranda.us/>"
__date__ = "2008-01-05"
__version__ = "1.0"
__credits__ = """Hereby released into the PUBLIC DOMAIN."""

def get_random_bytes(num_bytes, egd_path=None, blocking=True):
    """Gets random bytes from an EGD daemon.

    Attempts to return a string of num_bytes length with each character
    having a random byte value.  Requests for more than 255 bytes may
    result in multiple low-level requests to the EGD daemon.

    You may specify either a pathname to the EGD daemon's Unix domain
    socket, or a TCP port number, or a TCP address in the format
    "hostname:portnumber".  If you do not supply a path, a set of
    commonly used paths will be tried.

    If blocking is true, then the EGD daemon is queried in blocking mode,
    meaning that this function may be delayed in returning depending on
    how much entropy is in the EGD pool.  If blocking is false, then there
    is a chance you may not receive as much random data as requested,
    but you should not be indefinitely delayed.

    """
    if num_bytes < 1:
        return ''

    import socket
    if not egd_path:
        # No path given, try to find one at a known path
        import os, stat
        for egd_path in ['/dev/egd-pool','/var/run/egd-pool','/etc/egd-pool']:
            try:
                if os.stat(egd_path)[stat.ST_MODE] & stat.S_IFSOCK:
                    break
            except OSError:
                pass
        else:
            raise RuntimeError('No EGD socket found')
        addr = egd_path
        addr_family = socket.AF_UNIX
    else:
        try:
            portnum = int(egd_path)
        except ValueError:
            if ':' in egd_path and '/' not in egd_path:
                # A TCP socket to a "hostname:port" address
                addr_family = socket.AF_INET
                addr = egd_path.split(':', 1)
                try:
                    addr[1] = int(addr[1])
                except ValueError:
                    addr[1] = socket.getservbyname(addr[1], 'tcp')
                addr = tuple(addr)
            else:
                # Assume the string is a pathname to a Unix domain socket
                addr_family = socket.AF_UNIX
                addr = egd_path
        else:
            # Just a port number, this is a TCP socket to the localhost
            addr_family = socket.AF_INET
            addr = ('localhost', portnum)

    output = ''  # Accumulates the random bytes
    sok = socket.socket( addr_family, socket.SOCK_STREAM )
    try:
        sok.connect( addr )
        while len(output) < num_bytes:
            if blocking:
                cmd = '\x02'
            else:
                cmd = '\x01'
            cmd += chr(min(255, num_bytes - len(output)))
            sok.send( cmd )
            received = sok.recv(256)
            if len(received) == 0:
                if not blocking:
                    break # Entropy was drained, exit with what we have
            else:
                if blocking:
                    output += received
                else:
                    cnt = ord(received[0])
                    output += received[ 1 : 1+min(cnt, len(received)-1) ]
    finally:
        sok.close()
    return output


main_usage = \
"""Usage: egd.py [--path=path] [--blocking|--nonblocking] [--hex|--raw] [numbytes]

--path: specified path to the EGD socket.  May be a Unix path,
    or a TCP port number, or a "hostname:portnumber"

--hex | --raw: determines how the random bytes are output.
    The default (hex) is to output each byte in a hexadecimal
    encoded form.  With raw, each byte is output as-is.

--blocking | --nonblocking:  Determines which query command is made
    to the EGD daemon.  In blocking (the default), the process may
    have to wait until the EGD daemon has gathered enough entropy.
    In nonblocking, the process should return immediately although
    you may not get as many bytes (perhaps none) as you asked for.

"""

def main( argv ):
    """A command-line interface.

    For usage information run:
        python egd.py --help

    """
    import sys
    import getopt
    num_bytes = 1
    egd_path = None
    blocking = True
    as_hex = True
    try:
        opts, args = getopt.getopt( argv,
                                    'p:xr',
                                    ['path=','blocking','nonblocking',
                                     'hex','raw','help'] )
    except getopt.GetoptError:
        sys.stderr.write( main_usage )
        return 1
    for opt, val in opts:
        if opt == '--help':
            sys.stdout.write( main_usage )
            return 0
        elif opt in ('-p','--path'):
            egd_path = val
        elif opt == '--blocking':
            blocking = True
        elif opt == '--nonblocking':
            blocking = False
        elif opt in ('-x','--hex'):
            as_hex = True
        elif opt in ('-r','--raw'):
            as_hex = False

    if len(args) == 1:
        try:
            num_bytes = int(args[0])
        except ValueError:
            sys.stderr.write( main_usage )
            return 1
    elif len(args) > 1:
        sys.stderr.write( main_usage )
        return 1

    output = get_random_bytes( num_bytes, egd_path, blocking )
    if as_hex:
        hex = ''.join(['%02x'%ord(c) for c in output])
        sys.stdout.write(hex)
        sys.stdout.write('\n')
    else:
        sys.stdout.write(output)
    return 0


if __name__ == '__main__':
    import sys
    rc = main( sys.argv[1:] )
    if rc != 0:
        sys.exit(rc)

# end of file
