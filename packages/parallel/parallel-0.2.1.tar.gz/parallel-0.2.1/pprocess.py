#!/usr/bin/env python

"""
A simple parallel processing API for Python, inspired somewhat by the thread
module, slightly less by pypar, and slightly less still by pypvm.

Copyright (C) 2005 Paul Boddie <paul@boddie.org.uk>

This software is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with this library; see the file LICENCE.txt
If not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

--------

Thread-style Processing
-----------------------

To create new processes to run a function or any callable object, specify the
"callable" and any arguments as follows:

channel = start(fn, arg1, arg2, named1=value1, named2=value2)

This returns a channel which can then be used to communicate with the created
process. Meanwhile, in the created process, the given callable will be invoked
with another channel as its first argument followed by the specified arguments:

def fn(channel, arg1, arg2, named1, named2):
    # Read from and write to the channel.
    # Return value is ignored.
    ...

Fork-style Processing
---------------------

To create new processes in a similar way to that employed when using os.fork
(ie. the fork system call on various operating systems), use the following
method:

channel = create()
if channel.pid == 0:
    # This code is run by the created process.
    # Read from and write to the channel to communicate with the
    # creating/calling process.
    # An explicit exit of the process may be desirable to prevent the process
    # from running code which is intended for the creating/calling process.
    ...
else:
    # This code is run by the creating/calling process.
    # Read from and write to the channel to communicate with the created
    # process.
    ...

Message Exchanges
-----------------

When creating many processes, each providing results for the consumption of the
main process, the collection of those results in an efficient fashion can be
problematic: if some processes take longer than others, and if we decide to read
from those processes when they are not ready instead of other processes which
are ready, the whole activity will take much longer than necessary.

One solution to the problem of knowing when to read from channels is to create
an Exchange object, optionally initialising it with a list of channels through
which data is expected to arrive:

exchange = Exchange()           # populate the exchange later
exchange = Exchange(channels)   # populate the exchange with channels

We can add channels to the exchange using the add method:

exchange.add(channel)

To test whether an exchange is active - that is, whether it is actually
monitoring any channels - we can use the active method which returns all
channels being monitored by the exchange:

channels = exchange.active()

We may then check the exchange to see whether any data is ready to be received;
for example:

for channel in exchange.ready():
    # Read from and write to the channel.
    ...

If we do not wish to wait indefinitely for a list of channels, we can set a
timeout value as an argument to the ready method (as a floating point number
specifying the timeout in seconds, where 0 means a non-blocking poll as stated
in the select module's select function documentation).

Signals and Waiting
-------------------

When created/child processes terminate, one would typically want to be informed
of such conditions using a signal handler. Unfortunately, Python seems to have
issues with restartable reads from file descriptors when interrupted by signals:

http://mail.python.org/pipermail/python-dev/2002-September/028572.html
http://twistedmatrix.com/bugs/issue733

Select and Poll
---------------

The exact combination of conditions indicating closed pipes remains relatively
obscure. Here is a message/thread describing them (in the context of another
topic):

http://twistedmatrix.com/pipermail/twisted-python/2005-February/009666.html

It would seem, from using sockets and from studying the asyncore module, that
sockets are more predictable than pipes.
"""

__version__ = "0.2.1"

import os
import sys
import select
import socket

try:
    import cPickle as pickle
except ImportError:
    import pickle

class AcknowledgementError(Exception):
    pass

class Channel:

    "A communications channel."

    def __init__(self, pid, read_pipe, write_pipe):

        """
        Initialise the channel with a process identifier 'pid', a 'read_pipe'
        from which messages will be received, and a 'write_pipe' into which
        messages will be sent.
        """

        self.pid = pid
        self.read_pipe = read_pipe
        self.write_pipe = write_pipe
        self.closed = 0

    def __del__(self):

        # Since signals don't work well with I/O, we close pipes and wait for
        # created processes upon finalisation.

        self.close()

    def close(self):

        "Explicitly close the channel."

        if not self.closed:
            self.closed = 1
            self.read_pipe.close()
            self.write_pipe.close()
            #self.wait(os.WNOHANG)

    def wait(self, options=0):

        "Wait for the created process, if any, to exit."

        if self.pid != 0:
            try:
                os.waitpid(self.pid, options)
            except OSError:
                pass

    def _send(self, obj):

        "Send the given object 'obj' through the channel."

        pickle.dump(obj, self.write_pipe)
        self.write_pipe.flush()

    def send(self, obj):

        """
        Send the given object 'obj' through the channel. Then wait for an
        acknowledgement. (The acknowledgement makes the caller wait, thus
        preventing processes from exiting and disrupting the communications
        channel and losing data.)
        """

        self._send(obj)
        if self._receive() != "OK":
            raise AcknowledgementError, obj

    def _receive(self):

        "Receive an object through the channel, returning the object."

        obj = pickle.load(self.read_pipe)
        if isinstance(obj, Exception):
            raise obj
        else:
            return obj

    def receive(self):

        """
        Receive an object through the channel, returning the object. Send an
        acknowledgement of receipt. (The acknowledgement makes the sender wait,
        thus preventing processes from exiting and disrupting the communications
        channel and losing data.)
        """

        try:
            obj = self._receive()
            return obj
        finally:
            self._send("OK")

class Exchange:

    """
    A communications exchange that can be used to detect channels which are
    ready to communicate.
    """

    def __init__(self, channels=None, autoclose=1):

        """
        Initialise the exchange with an optional list of 'channels'. If the
        optional 'autoclose' parameter is set to a false value, channels will
        not be closed automatically when they are removed from the exchange - by
        default they are closed when removed.
        """

        self.autoclose = autoclose
        self.readables = {}
        self.poller = select.poll()
        for channel in channels or []:
            self.add(channel)

    def add(self, channel):

        "Add the given 'channel' to the exchange."

        self.readables[channel.read_pipe.fileno()] = channel
        self.poller.register(channel.read_pipe.fileno(), select.POLLIN | select.POLLHUP | select.POLLNVAL | select.POLLERR)

    def active(self):

        "Return a list of active channels."

        return self.readables.values()

    def ready(self, timeout=None):

        """
        Wait for a period of time specified by the optional 'timeout' (or until
        communication is possible) and return a list of channels which are ready
        to be read from.
        """

        fds = self.poller.poll(timeout)
        readables = []
        for fd, status in fds:
            channel = self.readables[fd]

            # Remove ended/error channels.

            if status & (select.POLLHUP | select.POLLNVAL | select.POLLERR):
                self.remove(channel)

            # Record readable channels.

            elif status & select.POLLIN:
                readables.append(channel)

        return readables

    def remove(self, channel):

        """
        Remove the given 'channel' from the exchange.
        """

        del self.readables[channel.read_pipe.fileno()]
        self.poller.unregister(channel.read_pipe.fileno())
        if self.autoclose:
            channel.close()
            channel.wait()

def create():

    """
    Create a new process, returning a communications channel to both the
    creating process and the created process.
    """

    parent, child = socket.socketpair()
    for s in [parent, child]:
        s.setblocking(1)

    pid = os.fork()
    if pid == 0:
        parent.close()
        return Channel(pid, child.makefile("r"), child.makefile("w"))
    else:
        child.close()
        return Channel(pid, parent.makefile("r"), parent.makefile("w"))

def start(callable, *args, **kwargs):

    """
    Create a new process which shall start running in the given 'callable'.
    Return a communications channel to the creating process, and supply such a
    channel to the created process as the 'channel' parameter in the given
    'callable'. Additional arguments to the 'callable' can be given as
    additional arguments to this function.
    """

    channel = create()
    if channel.pid == 0:
        try:
            try:
                callable(channel, *args, **kwargs)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                channel.send(exc_value)
        finally:
            channel.close()
            sys.exit(0)
    else:
        return channel

def waitall():

    "Wait for all created processes to terminate."

    try:
        while 1:
            os.wait()
    except OSError:
        pass

# vim: tabstop=4 expandtab shiftwidth=4
