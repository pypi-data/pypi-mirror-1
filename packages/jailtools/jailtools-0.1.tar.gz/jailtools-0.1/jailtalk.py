#!/usr/bin/env python

"""
A simple jail communications mechanism, permitting client programs to request
the execution of jailed programs via a jail server.

Copyright (C) 2006, 2007 Paul Boddie <paul@boddie.org.uk>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

__version__ = "0.1"

import SocketServer
import socket
import subprocess
import os, shutil
import sys
import pprocess

jailtools_dir = os.path.split(sys.argv[0])[0]

class JailServer(SocketServer.ForkingMixIn, SocketServer.UnixStreamServer):

    "A jail server which forks processes to execute jailed programs."

    def server_bind(self):

        "Change the permissions on the bound socket."

        SocketServer.UnixStreamServer.server_bind(self)
        os.chown(self.server_address, self.RequestHandlerClass.uid, self.RequestHandlerClass.gid)

    # API extension.

    def show_options(self):
        self.RequestHandlerClass.show_options()

class JailHandlerFactory:

    "A factory class creating handler objects for the server."

    def __init__(self, args):

        "Initialise the factory with the given 'args'."

        self.args = args
        self.uid = int(args["uid"])
        self.gid = int(args["gid"])

    def __call__(self, request, client_address, server):

        "Act as a factory for the server objects."

        handler = JailHandler(request, client_address, server, self.args)
        return handler

    def show_options(self):
        items = self.args.items()
        items.sort()
        for item in items:
            print "%20s:%s" % item

class JailHandler(SocketServer.StreamRequestHandler):

    "A class executing jailed programs."

    opt_names = ("memory-limit", "cpu-limit", "file-limit", "file-size-limit", "process-limit", "enable-modules")
    program_filename = "program.py"
    rbufsize = 0

    def __init__(self, request, client_address, server, args):

        """
        Initialise the handler with the given 'request', 'client_address' and
        'server', together with the jail configuration 'args'.
        """

        self.directory = args["directory"]
        self.uid = int(args["uid"])
        self.gid = int(args["gid"])
        self.reuse_jails = args.has_key("reuse-jails")

        # Command options.

        self.opts = [("--%s=%s" % (name, args[name])) for name in self.opt_names if args.get(name)]

        # Start the handler.

        SocketServer.StreamRequestHandler.__init__(self, request, client_address, server)

    def handle(self):

        "Dispatch the request to the given program."

        header = self.rfile.readline()
        jail_name = self.rfile.read(int(header))
        header = self.rfile.readline()
        program_text = self.rfile.read(int(header))

        # Get the exact jail location.

        jail_directory = os.path.abspath(os.path.join(self.directory, jail_name))
        valid_directory = os.path.abspath(os.path.join(self.directory, ""))

        if not jail_directory.startswith(valid_directory):
            return # NOTE: Should signal error.

        if os.path.exists(jail_directory):
            if not self.reuse_jails:
                return # NOTE: Should signal error.
        else:
            os.mkdir(jail_directory)
            os.chown(jail_directory, self.uid, self.gid)

        try:
            # Write the program to the jail.

            program_location = os.path.join(jail_directory, self.program_filename)
            f = open(program_location, "wb")
            try:
                f.write(program_text)
            finally:
                f.close()

            # Set the program permissions.

            os.chown(program_location, self.uid, self.gid)

            # Do not enter the jail in this process - we have too many resources
            # available for possible mischief.

            jailtools_py = os.path.join(jailtools_dir, "jailtools.py")

            cmd = map(str, [
                sys.executable, "-u", jailtools_py,     # Python in unbuffered mode
                jail_directory, self.uid,               # User credentials
                "--exec", self.program_filename         # The program
                ] + self.opts                           # Resource limits
                )
            print cmd

            # Communicate with the jailed process.

            opener = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            jail_channel = pprocess.Channel(opener.pid, opener.stdout, opener.stdin)
            jail_error_channel = pprocess.Channel(opener.pid, opener.stderr, opener.stdin)
            client_channel = pprocess.Channel(0, self.rfile, self.wfile)
            print opener.pid

            # Drop down to being the jailed process's user.

            os.setuid(self.uid)

            # While communications are active, relay the messages.

            try:
                multiplex([jail_channel, jail_error_channel], client_channel)
            finally:
                print opener.pid, "completed"
                #os.waitpid(opener.pid, 0)

        finally:
            if not self.reuse_jails:
                shutil.rmtree(jail_directory)

# Common functions.

def multiplex(local_channels, remote_channel, keep_local_open=0):

    "Multiplex the 'local_channels' and 'remote_channel'."

    exchange = pprocess.Exchange(local_channels + [remote_channel], autoclose=0)

    # If any of the channels stop working, stop multiplexing and finish.

    while len(exchange.active()) > 1:

        # Service each ready channel.

        for channel in exchange.ready():

            # Input from local channels is encoded and sent through the remote
            # channel.

            if channel in local_channels:
                s = channel.read_pipe.read(1)
                s = remote_encode(local_channels.index(channel), s)
                remote_channel.write_pipe.write(s)
                remote_channel.write_pipe.flush()

            # Input from the remote channel is decoded, either causing the
            # closure of the channel to the local process (which will hopefully
            # notice), or the sending of the input to the local process.

            elif channel is remote_channel:
                s = channel.read_pipe.readline()
                if not s:
                    continue
                n = int(s)
                s = channel.read_pipe.readline()
                if not s or not int(s):
                    if not keep_local_open:
                        local_channels[n].write_pipe.close()
                else:
                    s = channel.read_pipe.read(int(s))
                    local_channels[n].write_pipe.write(s)
                    local_channels[n].write_pipe.flush()

    # Obtain all input from local channels.

    for local_channel in local_channels:
        if local_channel in exchange.removed:
            s = local_channel.read_pipe.read()
            s = remote_encode(local_channels.index(local_channel), s)
            remote_channel.write_pipe.write(s)
            remote_channel.write_pipe.flush()

    # Deliver any remote input to the local process.

    if remote_channel in exchange.removed:

        # Keep reading: the protocol should save us here.

        while 1:
            s = remote_channel.read_pipe.readline()
            if not s:
                break
            n = int(s)
            s = remote_channel.read_pipe.readline()
            if not s or not int(s):
                if not keep_local_open:
                    local_channels[n].write_pipe.close()
                break
            else:
                s = remote_channel.read_pipe.read(int(s))
                local_channels[n].write_pipe.write(s)
                local_channels[n].write_pipe.flush()

def remote_encode(n, s):

    """
    For channel 'n', encode 's' for remote sending, using a decimal length plus
    a newline character followed by the value of 's' itself.
    """

    if not s:
        return "%d\n0\n" % n
    else:
        return "%d\n%d\n%s" % (n, len(s), s)

# Server functions.

def start_server(address, args, force=0):

    """
    Start a server listening on the given 'address' and configured using the
    given 'args' whose entries must include the following:

    directory       The jail directory
    uid             The user identity for the executed programs
    gid             The group identity for the executed programs

    Additional entries in 'args' may also include the following:

    memory-limit    The memory limit based on a multiple of the initial
                    process size
    cpu-limit       The CPU time in seconds
    file-limit      The number of open files
    file-size-limit The maximum size of created files in bytes
    process-limit   The number of child processes
    module-names    A comma-separated list of permitted, preloaded modules for
                    the executed programs
    reuse-jails     If set, permits the re-use of jails so that their contents
                    may be inspected after the exit of a jailed process and
                    subsequently re-used

    If the optional 'force' parameter is set to a true value, unlink any file
    which already exists representing 'address'.
    """

    if force and os.path.exists(address):
        os.unlink(address)
    factory = JailHandlerFactory(args)
    server = JailServer(address, factory)
    return server

# Client functions.

def open_jail(address, name, program_text):

    """
    Send to 'address' the given jail 'name' and 'program_text', returning a
    2-tuple of file-like objects (to_program, from_program).
    """

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(address)
    f = s.makefile("wb", 0)
    f2 = s.makefile("rb", 0)
    f.write("%s\n" % len(name))
    f.write(name)
    f.write("%s\n" % len(program_text))
    f.write(program_text)
    f.flush()
    return f, f2

def popen2(address, name, filename):

    """
    Using the given 'address' and jail 'name', invoke the program with the given
    'filename' and return a 2-tuple of file-like objects (to_program,
    from_program). Note that these objects use a special protocol and do not
    represent the exact streams that would be used to communicate with a normal
    subprocess.
    """

    f = open(filename, "rb")
    try:
        return open_jail(address, name, f.read())
    finally:
        f.close()

def console(address, name, filename):

    """
    Using the given 'address' and jail 'name', invoke the program with the given
    'filename' and interact with it, having standard input relayed to the
    program, and having the program's standard output and error relayed to this
    process's standard output.
    """

    to_program, from_program = popen2(address, name, filename)
    jail_channel = pprocess.Channel(1, from_program, to_program)
    stdout_channel = pprocess.Channel(0, sys.stdin, sys.stdout)
    stderr_channel = pprocess.Channel(0, sys.stdin, sys.stderr)
    multiplex([stdout_channel, stderr_channel], jail_channel, 1)

# Internal convenience function.

def set_opts(self, d, opt, value):
    if value is not None:
        d[opt] = value

help_text = """
Please specify one of the following collections of arguments:

The --server option, followed by the address (a filename at which a
UNIX domain socket will be created), the directory in which jailed
program environments will be created, the uid of jailed processes, the
gid of the jailed processes, and a number of optional arguments
configuring the jail environments. The uid must not be zero.

The address of the server (a filename at which a UNIX domain socket
has been created), the name of the jailed program's environment (a
directory inside which the program will run), and the filename of a
program to be uploaded and run in that environment.

See the jailtools module for descriptions of the other arguments.
"""

syntax_description = """
( --server [ --force ] <address> <directory> <uid> <gid> [ --reuse-jails ]
  [ --memory-limit=MULTIPLE ] [ --cpu-limit=TIME ] [ --file-limit=NFILES ]
  [ --file-size-limit=SIZE ] [ --process-limit=NPROCESSES ]
  [ --enable-modules=NAMES ] )
| ( <address> <name> <program> )
"""

# Main program.

if __name__ == "__main__":
    import cmdsyntax

    # Get the jail location and jailed user identity.

    syntax = cmdsyntax.Syntax(syntax_description)
    syntax_matches = syntax.get_args(sys.argv[1:])

    try:
        args = syntax_matches[0]
    except IndexError:
        print "Syntax:"
        print syntax_description
        print help_text
        print "Examples:"
        print
        print sys.executable, "-u", sys.argv[0], "--server", "/tmp/address", "/tmp/test", "1000", "1000"
        print sys.executable, "-u", sys.argv[0], "--server", "/tmp/address", "/tmp/test", "1000", "1000", "--memory-limit=2"
        print sys.executable, "-u", sys.argv[0], "--server", "/tmp/address", "/tmp/test", "1000", "1000", "--file-limit=0"
        print sys.executable, "-u", sys.argv[0], "/tmp/address", "jp", "program.py"
        print
        print "Important:"
        print
        print "This program must be run in unbuffered mode either using the -u option"
        print "when running", sys.executable, "(as shown above) or by setting the"
        print "PYTHONUNBUFFERED environment variable."
        print
        sys.exit(1)

    if args.has_key("server"):

        s = start_server(args["address"], args, force=args.has_key("force"))

        print "Starting server with the following options:"
        s.show_options()
        s.serve_forever()

    else:
        console(args["address"], args["name"], args["program"])

# vim: tabstop=4 expandtab shiftwidth=4
