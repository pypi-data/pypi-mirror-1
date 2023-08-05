#!/usr/bin/env python

"""
A simple parallel processing API for Python, inspired somewhat by the thread
module, slightly less by pypar, and slightly less still by pypvm.

Copyright (C) 2005, 2006, 2007 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

--------

Thread-style Processing
-----------------------

To create new processes to run a function or any callable object, specify the
"callable" and any arguments as follows:

channel = pprocess.start(fn, arg1, arg2, named1=value1, named2=value2)

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

channel = pprocess.create()
if channel.pid == 0:
    # This code is run by the created process.
    # Read from and write to the channel to communicate with the
    # creating/calling process.
    # An explicit exit of the process may be desirable to prevent the process
    # from running code which is intended for the creating/calling process.
    ...
    pprocess.exit(channel)
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

exchange = pprocess.Exchange()           # populate the exchange later
exchange = pprocess.Exchange(channels)   # populate the exchange with channels

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

class MyExchange(pprocess.Exchange):
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

Or we can request that the exchange create a channel on our behalf:

channel = exchange.create()

We can even start processes and monitor channels without ever handling the
channel ourselves:

exchange.start(fn, arg1, arg2, named1=value1, named2=value2)

We can explicitly wait for "free space" for channels by calling the wait method,
although the start and add_wait methods make this less interesting:

exchange.wait()

Finally, when finishing the computation, we can choose to merely call the finish
method and have the remaining data processed automatically:

exchange.finish()

Clearly, this approach is less flexible but more convenient than the raw message
exchange API as described above. However, it permits much simpler and clearer
code.

Exchanges as Queues
-------------------

Instead of having to subclass the pprocess.Exchange class and to define the
store_data method, it might be more desirable to let the exchange manage the
communications between created and creating processes and to let the creating
process just consume received data as it arrives, without particular regard for
the order of the received data - perhaps the creating process has its own way of
managing such issues.

For such situations, the Queue class may be instantiated and channels added to
the queue using the various methods provided:

queue = pprocess.Queue(limit=10)
channel = queue.create()
if channel:
    # Do some computation.
    pprocess.exit(channel)

The results can then be consumed by treating the queue like an iterator:

for result in queue:
    # Capture each result.

This approach does not, of course, require the direct handling of channels. One
could instead use the start method on the queue to create processes and to
initiate computations (since a queue is merely an enhanced exchange with a
specific implementation of the store_data method).

Exchanges as Maps
-----------------

Where the above Queue class appears like an attractive solution for the
management of the results of computations, but where the order of their
consumption by the creating process remains important, the Map class may offer a
suitable way of collecting and accessing results:

results = pprocess.Map(limit=10)
for value in inputs:
    results.start(fn, args)

The results can then be consumed in an order corresponding to the order of the
computations which produced them:

for result in results:
    # Process each result.

Internally, the Map object records a particular ordering of channels, ensuring
that the received results can be mapped to this ordering, and that the results
can be made available with this ordering preserved.

Managed Callables
-----------------

A further simplification of the above convenient use of message exchanges
involves the creation of callables (eg. functions) which are automatically
monitored by an exchange. We create such a callable by calling the manage method
on an exchange:

myfn = exchange.manage(fn)

This callable can then be invoked instead of using the exchange's start method:

myfn(arg1, arg2, named1=value1, named2=value2)

The exchange's finish method can be used as usual to process incoming data.

Making Existing Functions Parallel
----------------------------------

In making a program parallel, existing functions which only return results can
be manually modified to accept and use channels to communicate results back to
the main process. However, a simple alternative is to use the MakeParallel class
to provide a wrapper around unmodified functions which will return the results
from those functions in the channels provided. For example:

fn = pprocess.MakeParallel(originalfn)

Map-style Processing
--------------------

In situations where a callable would normally be used in conjunction with the
Python built-in map function, an alternative solution can be adopted by using
the pmap function:

pprocess.pmap(fn, sequence)

Here, the sequence would have to contain elements that each contain the required
parameters of the specified callable, fn. Note that the callable does not need
to be a parallel-aware function which has a channel argument: the pmap function
automatically wraps the given callable internally.

Reusing Processes and Channels
------------------------------

So far, all parallel computations have been done with newly-created processes.
However, this can seem somewhat inefficient, especially if processes are being
continually created and destroyed (although if this happens too often, the
amount of work done by each process may be too little, anyway). One solution is
to retain processes after they have done their work and request that they
perform more work for each new parallel task or invocation. To enable the reuse
of processes in this way, a special keyword argument may be specified when
creating Exchange objects (and subclasses such as Map and Queue). For example:

exchange = MyExchange(limit=10, reuse=1) # reuse up to 10 processes

Code invoked through such exchanges must be aware of channels and be constructed
in such a way that it does not terminate after sending a result back to the
creating process. Instead, it should repeatedly wait for subsequent sets of
parameters (compatible with those either in the signature of a callable or with
the original values read from the channel). Reusable code is terminated when the
special value of None is sent from the creating process to the created process,
indicating that no more parameters will be sent; this should cause the code to
terminate.

Making Existing Functions Parallel and Reusable
-----------------------------------------------

An easier way of making reusable code sections for parallel use is to employ the
MakeReusable class to wrap an existing callable:

fn = pprocess.MakeReusable(originalfn)

This wraps the callable in a similar fashion to MakeParallel, but provides the
necessary mechanisms described above for reusable code.

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

__version__ = "0.3"

import os
import sys
import select
import socket

try:
    import cPickle as pickle
except ImportError:
    import pickle

# Communications.

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

# Management of processes and communications.

class Exchange:

    """
    A communications exchange that can be used to detect channels which are
    ready to communicate. Subclasses of this class can define the 'store_data'
    method in order to enable the 'add_wait', 'wait' and 'finish' methods.
    """

    def __init__(self, channels=None, limit=None, reuse=0, autoclose=1):

        """
        Initialise the exchange with an optional list of 'channels'.

        If the optional 'limit' is specified, restrictions on the addition of
        new channels can be enforced and observed through the 'add_wait', 'wait'
        and 'finish' methods. To make use of these methods, create a subclass of
        this class and define a working 'store_data' method.

        If the optional 'reuse' parameter is set to a true value, channels and
        processes will be reused for waiting computations.

        If the optional 'autoclose' parameter is set to a false value, channels
        will not be closed automatically when they are removed from the exchange
        - by default they are closed when removed.
        """

        self.limit = limit
        self.reuse = reuse
        self.autoclose = autoclose
        self.waiting = []
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

    def start_waiting(self, channel):

        """
        Start a waiting process given the reception of data on the given
        'channel'.
        """

        if self.waiting:
            callable, args, kw = self.waiting.pop()

            # Try and reuse existing channels if possible.

            if self.reuse:

                # Re-add the channel - this may update information related to
                # the channel in subclasses.

                self.add(channel)
                channel.send((args, kw))
            else:
                self.add(start(callable, *args, **kw))

        # Where channels are being reused, but where no processes are waiting
        # any more, send a special value to tell them to quit.

        elif self.reuse:
            channel.send(None)

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
            self.start_waiting(channel)

    def store_data(self, channel):

        """
        Store incoming data from the specified 'channel'. In subclasses of this
        class, such data could be stored using instance attributes.
        """

        raise NotImplementedError, "store_data"

    # Convenience methods.

    def start(self, callable, *args, **kw):

        """
        Using pprocess.start, create a new process for the given 'callable'
        using any additional arguments provided. Then, monitor the channel
        created between this process and the created process.
        """

        if self.limit is not None and len(self.active()) >= self.limit:
            self.waiting.insert(0, (callable, args, kw))
            return

        self.add_wait(start(callable, *args, **kw))

    def create(self):

        """
        Using pprocess.create, create a new process and return the created
        communications channel to the created process. In the creating process,
        return None - the channel receiving data from the created process will
        be automatically managed by this exchange.
        """

        channel = create()
        if channel.pid == 0:
            return channel
        else:
            self.add_wait(channel)
            return None

    def manage(self, callable):

        """
        Wrap the given 'callable' in an object which can then be called in the
        same way as 'callable', but with new processes and communications
        managed automatically.
        """

        return ManagedCallable(callable, self)

class ManagedCallable:

    "A callable managed by an exchange."

    def __init__(self, callable, exchange):

        """
        Wrap the given 'callable', using the given 'exchange' to monitor the
        channels created for communications between this and the created
        processes. Note that the 'callable' must be parallel-aware (that is,
        have a 'channel' parameter). Use the MakeParallel class to wrap other
        kinds of callable objects.
        """

        self.callable = callable
        self.exchange = exchange

    def __call__(self, *args, **kw):

        "Invoke the callable with the supplied arguments."

        self.exchange.start(self.callable, *args, **kw)

# Abstractions and utilities.

class Map(Exchange):

    "An exchange which can be used like the built-in 'map' function."

    def __init__(self, *args, **kw):
        Exchange.__init__(self, *args, **kw)
        self.init()

    def init(self):

        "Remember the channel addition order to order output."

        self.channel_number = 0
        self.channels = {}
        self.results = []

    def add(self, channel):

        "Add the given 'channel' to the exchange."

        Exchange.add(self, channel)
        self.channels[channel] = self.channel_number
        self.channel_number += 1

    def start(self, callable, *args, **kw):

        """
        Using pprocess.start, create a new process for the given 'callable'
        using any additional arguments provided. Then, monitor the channel
        created between this process and the created process.
        """

        self.results.append(None) # placeholder
        Exchange.start(self, callable, *args, **kw)

    def create(self):

        """
        Using pprocess.create, create a new process and return the created
        communications channel to the created process. In the creating process,
        return None - the channel receiving data from the created process will
        be automatically managed by this exchange.
        """

        self.results.append(None) # placeholder
        return Exchange.create(self)

    def __call__(self, callable, sequence):

        "Wrap and invoke 'callable' for each element in the 'sequence'."

        if not isinstance(callable, MakeParallel):
            wrapped = MakeParallel(callable)
        else:
            wrapped = callable

        self.init()

        # Start processes for each element in the sequence.

        for i in sequence:
            self.start(wrapped, i)

        # Access to the results occurs through this object.

        return self

    def __getitem__(self, i):
        self.finish()
        return self.results[i]

    def __iter__(self):
        self.finish()
        return iter(self.results)

    def store_data(self, channel):

        "Accumulate the incoming data, associating results with channels."

        data = channel.receive()
        self.results[self.channels[channel]] = data
        del self.channels[channel]

class Queue(Exchange):

    """
    An exchange acting as a queue, making data from created processes available
    in the order in which it is received.
    """

    def __init__(self, *args, **kw):
        Exchange.__init__(self, *args, **kw)
        self.queue = []

    def store_data(self, channel):

        "Accumulate the incoming data, associating results with channels."

        data = channel.receive()
        self.queue.insert(0, data)

    def __iter__(self):
        return self

    def next(self):

        "Return the next element in the queue."

        if self.queue:
            return self.queue.pop()
        while self.active():
            self.store()
            if self.queue:
                return self.queue.pop()
        else:
            raise StopIteration

class MakeParallel:

    "A wrapper around functions making them able to communicate results."

    def __init__(self, callable):

        """
        Initialise the wrapper with the given 'callable'. This object will then
        be able to accept a 'channel' parameter when invoked, and to forward the
        result of the given 'callable' via the channel provided back to the
        invoking process.
        """

        self.callable = callable

    def __call__(self, channel, *args, **kw):

        "Invoke the callable and return its result via the given 'channel'."

        channel.send(self.callable(*args, **kw))

class MakeReusable(MakeParallel):

    """
    A wrapper around functions making them able to communicate results in a
    reusable fashion.
    """

    def __call__(self, channel, *args, **kw):

        "Invoke the callable and return its result via the given 'channel'."

        channel.send(self.callable(*args, **kw))
        t = channel.receive()
        while t is not None:
            args, kw = t
            channel.send(self.callable(*args, **kw))
            t = channel.receive()

# Utility functions.

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

def exit(channel):

    """
    Terminate a created process, closing the given 'channel'.
    """

    channel.close()
    os._exit(0)

def start(callable, *args, **kw):

    """
    Create a new process which shall start running in the given 'callable'.
    Additional arguments to the 'callable' can be given as additional arguments
    to this function.

    Return a communications channel to the creating process. For the created
    process, supply a channel as the 'channel' parameter in the given 'callable'
    so that it may send data back to the creating process.
    """

    channel = create()
    if channel.pid == 0:
        try:
            try:
                callable(channel, *args, **kw)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                channel.send(exc_value)
        finally:
            exit(channel)
    else:
        return channel

def waitall():

    "Wait for all created processes to terminate."

    try:
        while 1:
            os.wait()
    except OSError:
        pass

def pmap(callable, sequence, limit=None):

    """
    A parallel version of the built-in map function with an optional process
    'limit'. The given 'callable' should not be parallel-aware (that is, have a
    'channel' parameter) since it will be wrapped for parallel communications
    before being invoked.

    Return the processed 'sequence' where each element in the sequence is
    processed by a different process.
    """

    mymap = Map(limit=limit)
    return mymap(callable, sequence)

# vim: tabstop=4 expandtab shiftwidth=4
