#!/usr/bin/env python

"""
A simple parallel processing API for Python, inspired somewhat by the thread
module, slightly less by pypar, and slightly less still by pypvm.

Copyright (C) 2005, 2006, 2007 Paul Boddie <paul@boddie.org.uk>

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

The recommended styles of programming using pprocess involve the "Thread-style
Processing" and "Convenient Message Exchanges" sections below, although
developers may wish to read the "Message Exchanges" section for more details of
the API concerned, and the "Fork-style Processing" section may be of interest to
those with experience of large scale parallel processing systems.

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

Convenient Message Exchanges
----------------------------

A convenient form of message exchanges can be adopted by defining a subclass of
the Exchange class and defining a particular method:

class MyExchange(Exchange):
    def store_data(self, channel):
        data = channel.receive()
        # Do something with data here.

The exact operations performed on the received data might be as simple as
storing it on an instance attribute. To make use of the exchange, we would
instantiate it as usual:

exchange = MyExchange()         # populate the exchange later
exchange = MyExchange(limit=10) # set a limit for later population

The exchange can now be used in a simpler fashion than that shown above. We can
add channels as before using the add method, or we can choose to only add
channels if the specified limit of channels is not exceeded:

exchange.add(channel)           # add a channel as normal
exchange.add_wait(channel)      # add a channel, waiting if the limit would be
                                # exceeded

We can explicitly wait for "free space" for channels by calling the wait method:

exchange.wait()

Finally, when finishing the computation, we can choose to merely call the finish
method and have the remaining data processed automatically:

exchange.finish()

Clearly, this approach is less flexible but more convenient than the raw message
exchange API as described above. However, it permits much simpler and clearer
code.

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

Notes about poll implementations can be found here:

http://www.greenend.org.uk/rjk/2001/06/poll.html
"""

__version__ = "0.2.4"

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
    ready to communicate. Subclasses of this class can define the 'store_data'
    method in order to enable the 'add_wait', 'wait' and 'finish' methods.
    """

    def __init__(self, channels=None, limit=None, autoclose=1):

        """
        Initialise the exchange with an optional list of 'channels'.

        If the optional 'limit' is specified, restrictions on the addition of
        new channels can be enforced and observed through the 'add_wait', 'wait'
        and 'finish' methods. To make use of these methods, create a subclass of
        this class and define a working 'store_data' method.

        If the optional 'autoclose' parameter is set to a false value, channels
        will not be closed automatically when they are removed from the exchange
        - by default they are closed when removed.
        """

        self.limit = limit
        self.autoclose = autoclose
        self.readables = {}
        self.removed = []
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
        self.removed = []

        for fd, status in fds:
            channel = self.readables[fd]
            removed = 0

            # Remove ended/error channels.

            if status & (select.POLLHUP | select.POLLNVAL | select.POLLERR):
                self.remove(channel)
                self.removed.append(channel)
                removed = 1

            # Record readable channels.

            if status & select.POLLIN:
                if not (removed and self.autoclose):
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

    # Enhanced exchange methods involving channel limits.

    def add_wait(self, channel):

        """
        Add the given 'channel' to the exchange, waiting if the limit on active
        channels would be exceeded by adding the channel.
        """

        self.wait()
        self.add(channel)

    def wait(self):

        """
        Test for the limit on channels, blocking and reading incoming data until
        the number of channels is below the limit.
        """

        # If limited, block until channels have been closed.

        while self.limit is not None and len(self.active()) >= self.limit:
            self.store()

    def finish(self):

        """
        Finish the use of the exchange by waiting for all channels to complete.
        """

        while self.active():
            self.store()

    def store(self):

        "For each ready channel, process the incoming data."

        for channel in self.ready():
            self.store_data(channel)

    def store_data(self, channel):

        """
        Store incoming data from the specified 'channel'. In subclasses of this
        class, such data could be stored using instance attributes.
        """

        raise NotImplementedError, "store_data"

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
        return Channel(pid, child.makefile("r", 0), child.makefile("w", 0))
    else:
        child.close()
        return Channel(pid, parent.makefile("r", 0), parent.makefile("w", 0))

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
            os._exit(0)
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
