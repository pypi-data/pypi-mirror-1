#!/usr/bin/env python

"""
A simple chroot "jail" usage module/program providing the recommended way of
entering a chroot directory and setting the user identity. The provided
'enter_jail' function should be invoked as soon as possible in order to limit
the number of resources available to the jailed process.

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

--------

Using the module from a program:

import jailtools
jail = jailtools.Jail("/tmp/test", 1000)
jail.enter_jail()

Useful additional measures against mischievous programs:

jail.set_memory_limit(2)        # allow for twice the size of the current process
jail.set_cpu_limit(10)          # permit 10s CPU time before exit
jail.set_file_limit(4)          # permit 4 open files
jail.set_file_size_limit(10000) # set a 10000 byte limit on each created file
jail.set_process_limit(0)       # permit no child processes
"""

__version__ = "0.1"

import os, sys
import resource
import commands

# Status values.

class Status:

    "A class providing false values."

    def __init__(self, status):
        self.status = status
    def __str__(self):
        return self.status
    def __repr__(self):
        return "Status(%s)" % repr(self.status)
    def __nonzero__(self):
        return False

# Functions.

class Jail:

    def __init__(self, directory, uid, permit_root=0):

        """
        Initialise the jail at 'directory', assuming the identity specified by
        'uid'. If the optional 'permit_root' is specified and set to a true
        value, the 'uid' will not be rejected if set to zero: in such
        invocations, it is assumed that the caller knows of the risks involved
        in not immediately changing the user identity to a non-privileged user.
        """

        if not permit_root and uid == 0:
            raise ValueError, "Specify 'permit_root' as a true value when entering a jail with 'uid' set to zero."

        self.directory = directory
        self.uid = uid
        self.permit_root = permit_root

    def enter_jail(self, test_breakouts=1, paranoid=0):

        """
        Enter the jail using the details specified in the object's creation.

        If the optional 'test_breakouts' is set to a false value, a test of the
        jail will not be performed. Otherwise, the default behaviour is to test
        the jail by attempting to break out using a well-known technique for
        doing so, and to signal a compromise of the jail through a false return
        value (see below). Due to the behaviour of this technique when performed
        as the root user, the test must be suppressed if 'uid' is zero and
        'permit_root' is set in the creation of the jail object.

        If the optional 'paranoid' is set to a true value, the breakout test
        enabled by 'test_breakouts' will compare the file listings inside the
        jail to those in the jail location's parent directory in order to decide
        whether the breakout succeeded (by concluding that if the view inside
        the jail resembles the view outside of the jail then a breakout has
        occurred). This paranoia can potentially give false breakout reports in
        certain unlikely circumstances.

        Return whether the jail was successfully entered. If a false value is
        returned, it may be appropriate to abandon any subsequent operations and
        to exit the program immediately in order to prevent illegal access to
        resources outside the jail at potentially escalated privileges.
        """

        # Prevent breakouts if requested.

        if test_breakouts:
            plans = plan_breakout(self.directory)

        os.chdir(self.directory)
        os.chroot(self.directory)
        os.setuid(self.uid)

        # Test planned breakouts.

        if test_breakouts:
            return breakout_prevented(self.directory, plans, paranoid)

        return True

    def set_memory_limit(self, multiple):

        """
        Set the memory limit for the process according to the given 'multiple',
        where 1 represents the current memory usage, 2 represents twice the
        current memory usage, and so on. Floating point numbers for 'multiple'
        are permitted, but must be greater than one.
        """

        if multiple <= 1:
            raise ValueError, "The memory limit multiple must be greater than one."
        size_kilobytes = int(commands.getoutput("ps -p %d -o rss=" % os.getpid()))
        new_size_bytes = int(multiple * size_kilobytes * 1024)
        resource.setrlimit(resource.RLIMIT_AS, (new_size_bytes, new_size_bytes))

    def set_cpu_limit(self, t):

        """
        Set the CPU time limit to 't', where 't' is a length of time in seconds
        indicating the amount of time allowed for the process (in addition to
        the amount already used).
        """

        usage = resource.getrusage(resource.RUSAGE_SELF)
        cpu_used = usage[0] + usage[1]
        cpu_limit = int(cpu_used + t)
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))

    def set_file_limit(self, nfiles):

        "Set the limit on the number of open files to 'nfiles'."

        resource.setrlimit(resource.RLIMIT_NOFILE, (nfiles, nfiles))

    def set_file_size_limit(self, size):

        "Set the size limit on created files to 'size' bytes."

        resource.setrlimit(resource.RLIMIT_FSIZE, (size, size))

    def set_process_limit(self, nprocesses):

        """
        Set the limit on the number of new processes available to the jail's uid to
        'nprocesses'. This attempts to find out how many processes are already
        available to the user and then adds 'nprocesses' to the figure.
        """

        current_nprocesses = len(commands.getoutput("ps -u %s -o uid=" % self.uid).split("\n"))
        new_nprocesses = current_nprocesses + nprocesses + 1 # include the initial process
        resource.setrlimit(resource.RLIMIT_NPROC, (new_nprocesses, new_nprocesses))

# Internal functions.

def plan_breakout(directory):

    "Plan a breakout from the jail using the given 'directory'."

    parent_directory = os.path.abspath(os.path.join(directory, os.pardir))
    filenames = os.listdir(parent_directory)
    filenames.sort()
    return parent_directory, filenames

def breakout_prevented(directory, plans, paranoid=0, breakout_directory="__tunnel__"):

    """
    Attempt a breakout from 'directory' using the given 'plans' supplied by a
    call to the 'plan_breakout' function. Return whether the breakout was
    prevented, employing additional tests if the optional 'paranoid' parameter
    is set to a true value. The attempt makes use of the widely publicised
    method, employing a temporary directory whose name can be specified
    explicitly using the optional 'breakout_directory' parameter.
    """

    outside_cwd, outside_filenames = plans
    cd = None

    # Perform the technique.

    try:
        # Required step: make a directory.

        if not os.path.exists(breakout_directory):
            os.mkdir(breakout_directory)

        # Optional step: open the current directory.

        try:
            cd = os.open(os.curdir, os.O_RDONLY)
        except OSError:
            pass

        # Required step: enter the directory.

        os.chroot(breakout_directory)

        # Optional step: open the current directory.

        if cd is not None:
            os.fchdir(cd)

    # Ignore permissions issues and keep testing.

    except OSError:
        pass

    # Tidy up.

    if cd is not None:
        os.close(cd)

    try:
        if os.path.exists(breakout_directory):
            os.rmdir(breakout_directory)
    except OSError:
        pass

    # Return success if the current working directory is the chroot location.

    if os.getcwd() == directory:
        return Status("False: cwd changed")

    # Otherwise, attempt to ascend the directory hierarchy.

    for n in range(0, 2):
        os.chdir(os.pardir)

        # View the filesystem.

        new_filenames = os.listdir(os.curdir)
        new_filenames.sort()
        new_cwd = os.getcwd()

        # Determine whether the filesystem appears to be from outside the jail.

        if outside_cwd == new_cwd:
            return Status("False: cwd outside")
        if paranoid and outside_filenames == new_filenames:
            return Status("False: filenames outside")

    return True

# Utility functions for extra effect.

def remove_modules():
    for module_name in sys.modules.keys():
        if module_name not in ("__main__", "__builtin__", "sys"):
            del sys.modules[module_name]

def enable_modules(module_names):
    for module_name in module_names:
        if module_name:
            global_names[module_name] = __import__(module_name, global_names, {}, [])

# Help text.

help_text = """
Please specify the directory in which the jailed program will run, the
uid of the process, and a number of optional arguments configuring the
jail environment.

The uid must not be zero unless --permit-root is specified as an
additional argument after the uid. It is assumed that usage of this
program with the --permit-root argument is done with the knowledge of
the security risks associated with not immediately changing user
identity upon entering a chroot jail.

Additional tests assessing the jail's security can be performed by
providing the --test-breakouts and --paranoid arguments. Note that
this will prevent a jail being entered as a root user since the tests
will always fail in such a situation.

Resource limits can be specified for the jailed program as follows:

--memory-limit      The memory limit based on a multiple of the initial
                    process size
--cpu-limit         The CPU time in seconds
--file-limit        The number of open files
--file-size-limit   The maximum size of created files in bytes
--process-limit     The number of child processes

Modules allowed for use by the jailed programs (and preloaded) can be
controlled using the --enable-modules argument, consisting of a comma
separated list of module or package names.
"""

syntax_description = """
<directory> <uid>
[ --permit-root ] [ --test-breakouts ] [ --paranoid ]
[ --exec <program> ]
[ --memory-limit=MULTIPLE ] [ --cpu-limit=TIME ] [ --file-limit=NFILES ]
[ --file-size-limit=SIZE ] [ --process-limit=NPROCESSES ]
[ --enable-modules=NAMES ]
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
        print sys.argv[0], "/tmp/test", "1000"
        print sys.argv[0], "/tmp/test", "0", "--permit-root"
        print sys.argv[0], "/tmp/test", "1000", "--test-breakouts"
        print sys.argv[0], "/tmp/test", "1000", "--exec program.py"
        print sys.argv[0], "/tmp/test", "1000", "--exec program.py", "--memory-limit=2"
        print
        sys.exit(1)

    # Remove modules.

    remove_modules()

    # Enable stated modules.

    global_names = {}
    if args.has_key("enable-modules"):
        enable_modules(args["enable-modules"].split(","))

    # Enter the jail...

    try:
        jail = Jail(args["directory"], int(args["uid"]), args.has_key("permit-root"))

        if args.has_key("memory-limit"):
            jail.set_memory_limit(float(args["memory-limit"]))
        if args.has_key("cpu-limit"):
            jail.set_cpu_limit(int(args["cpu-limit"]))
        if args.has_key("file-limit"):
            jail.set_file_limit(int(args["file-limit"]))
        if args.has_key("file-size-limit"):
            jail.set_file_size_limit(int(args["file-size-limit"]))
        if args.has_key("process-limit"):
            jail.set_process_limit(int(args["process-limit"]))

        entered = jail.enter_jail(args.has_key("test-breakouts"), args.has_key("paranoid"))

    except ValueError:
        print help_text
        sys.exit(1)

    # Test the jail status.

    if not entered:
        print "Jail not entered, status is", entered
        sys.exit(1)

    # Either execute a program...

    if args.has_key("exec"):
        execfile(args["program"], global_names, global_names)

    # At this point, in an interactive session, the session should be jailed.

    else:
        print "Jail entered with uid", os.getuid(), "in", os.getcwd()

# vim: tabstop=4 expandtab shiftwidth=4
