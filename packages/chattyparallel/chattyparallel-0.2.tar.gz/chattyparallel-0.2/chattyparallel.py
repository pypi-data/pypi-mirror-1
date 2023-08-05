#!/usr/bin/env python2.5

"""chattyparallel - Run python code in forked processes with two-way communication,
                 inspired by Paul Boddie's Parallel http://www.python.org/pypi/parallel

To use this thing, you need a master process that subclasses ChattyParallel, and
worker child processes that subclass WorkerChannel. The master process sends tasks to
childs, and gets back results.

Suggestions and code review by Carlo C8E Miron, Lawrence Oluyede, Michele Campeotto.

Example:

>>> class TestAgent(WorkerChannel):
...     def __init__(self, *args, **kw):
...         super(TestAgent, self).__init__(*args, **kw)
...     def handle_message(self, msg):
...         self.logger.debug("received msg %s" % msg)
...         # echo the message back
...         self.send("msg '%s' received" % msg)
... 
>>> class TestParallel(ChattyParallel):
...     def __init__(self, *args, **kw):
...         super(TestParallel, self).__init__(*args, **kw)
...     def receive(self, channel, data):
...         super(TestParallel, self).receive(channel, data)
...         # handle the result here
... 
>>> l = logging.getLogger('chattytest')
>>> l.setLevel(logging.CRITICAL)
>>> h = logging.StreamHandler(sys.stdout)
>>> h.setLevel(logging.CRITICAL)
>>> h.setFormatter(logging.Formatter('%(asctime)s %(process)d %(levelname)-8s %(message)s'))
>>> l.addHandler(h)
>>> tasks = ["message no. %s" % i for i in xrange(15)]
>>> p = ChattyParallel(tasks, logger=l)
>>> num_tasks = len(p.tasks)
>>> for i in range(2):
...     pid = p.start_channel(TestAgent)
... 
>>> p.loop(5)
>>> p.done == num_tasks == 15
True
>>> tasks = ["message no. %s" % i for i in xrange(15)]
>>> p = TestParallel(tasks, logger=l)
>>> num_tasks = len(p.tasks)
>>> for i in range(2):
...     pid = p.start_channel(TestAgent)
... 
>>> p.loop(5)
>>> p.done == num_tasks == 15
True
>>> 
                 
"""

__author__ = "Ludovico Magnocavallo <ludo\x40qix\x2eit>"
__copyright__ = "Copyright 2007, Ludovico Magnocavallo"
__license__ = "MIT"
__version__ = "0.2"
__revision__ = "$LastChangedRevision: 1401 $"[22:-2]
__date__ = "$LastChangedDate: 2007-04-03 15:34:47 +0200 (Tue, 03 Apr 2007) $"[18:-2]

import os
import sys
import socket
import select
import struct
import errno
import traceback
import logging
try:
    import cPickle as pickle
except ImportError:
    import pickle
from collections import deque

BUFSIZE = 65536

class ChannelError(Exception): pass
class ChannelDisconnect(Exception): pass

class Channel(object):
    """Base class to handle two-way communications between processes. This type
    of channel has no internal message queue, so it processes messages serially,
    and no polling loop, as it is not needed for the channels used by the
    controlling process.
    
    Keyword arguments:
        sock   -- the opened socket to use for communication
        poll   -- a select.poll() object to use to monitor the socket state
        pid    -- the pid of the process using this channel
        logger -- a logging Logger instance
    """
    def __init__(self, sock, poll=None, pid=None, logger=None):
        self._sock = sock
        self._fileno = sock.fileno()
        self._poll = poll or select.poll()
        self.logger = logger or logging.getLogger('top100.crawler')
        self._quit = False
        self.quit_sent = False
        self._rb = ''
        self._msglen = None
        self._wb = None
        self.pid = os.getpid()
        self.other_pid = pid
        self.logger.debug("%s registering %s" % (self, self._fileno))
        self._poll.register(self._fileno, select.POLLIN | select.POLLPRI)
        self.logger.debug("%s started" % self)
       
    def _handle_message(self, message):
        if msg == 0:
            # QUIT message, we are reading messages serially so we can quit
            # if we are not writing, as this is the last message
            self.logger.debug("channel %s received a QUIT message" % self)
            if self._wb:
                self._quit = True
            else:
                raise ChannelDisconnect, "quitting"
        self.handle_message(message)
        
    def handle_message(self, message):
        """Received messages are passed to this method, so you need to override
        it in your derived classes.
        """
        raise NotImplementedError, "override handle_message()"
       
    def send(self, data):
        """Schedule an outgoing message for delivery.
        """
        data = pickle.dumps(data)
        msg = "%s%s" % (struct.pack("!L", len(data)), data)
        if self._wb:
            self._wb = "%s%s" % (self._wb, msg)
        else:
            self._wb = msg
        self._poll.register(self._sock, select.POLLIN | select.POLLPRI | select.POLLOUT)
       
    def read(self):
        """Read from this channel's socket. This method is called from the polling
        loop, which may be run by the class owning the channel, like in the
        controlling process.
        """
        try:
            data = self._sock.recv(BUFSIZE)
        except socket.error, e:
            if e.args and e.args[0] == errno.EAGAIN:
                self.logger.info("EAGAIN in channel %s, resource temporarily unavailable" % self)
                return
            self.logger.warning("socket error %s in channel %s" % (e, self))
            raise ChannelDisconnect, "socket error %s in channel %s" % (e, self)
        if not data:
            self.logger.debug("no data in channel %s" % self.pid)
            raise ChannelDisconnect, "no data in channel %s" % self.pid
        while True:
            msglen = self._msglen
            data = "%s%s" % (self._rb, data)
            if not msglen and len(data) >= 4:
                self.logger.debug("getting msglen")
                msglen = struct.unpack('!L', data[:4])[0]
                data = data[4:]
            if not msglen or len(data) < msglen:
                self._msglen = msglen
                self._rb = data
                break
            else:
                msg = pickle.loads(data[:msglen])
                data = data[msglen:]
                self._msglen = None
                self._rb = data
                data = ''
                try:
                    self._handle_message(msg)
                except Exception, e:
                    self.logger.critical("unhandled exception in channel %s: %s" % (self, traceback.format_exc()))
                    self.send(e)
        
    def write(self):
        """Write to this channel's socket. This method is called from the polling
        loop, which may be run by the class owning the channel, like in the
        controlling process.
        """
        wb = self._wb
        try:
            sent = self._sock.send(wb)
        except socket.error, e:
            self.logger.warning("socket error while writing in channel %s, socket error %s" % (self, e))
            raise ChannelDisconnect, "socket error while writing in channel %s, socket error %s" % (self, e)
        if sent == 0:
            self.logger.warning("nothing written to socket in channel %s" % self)
            raise ChannelDisconnect, "nothing written to socket in channel %s" % self
        if sent < len(wb):
            self._wb = wb[sent:]
        else:
            self._wb = ''
            self._poll.register(self._sock, select.POLLIN | select.POLLPRI)
            if self._quit:
                raise ChannelDisconnect, "quitting"
        
    def disconnect(self, e=None):
        """Disconnect this channel, closing the socket and exiting the child
        process."""
        self.logger.info("disconnecting channel %s" % self)
        try:
            self._poll.unregister(self._fileno)
        except KeyError:
            self.logger.debug("unknown fileno %s when disconnecting")
        self._sock.close()
        if e:
            raise ChannelError, str(e)
        os._exit(0)
            
    def __repr__(self):
        return "<Channel from %s to %s fd %s>" % (self.pid, self.other_pid, self._fileno)
    
class MasterChannel(Channel):
    """Channel type used by the controlling process, with no polling loop and no
    disconnection. It accepts the master process controller as its first argument,
    to grab its receive() method and use it as a callback to process incoming messages.
    """
    
    def __init__(self, master, sock, *args, **kw):
        super(MasterChannel, self).__init__(sock, *args, **kw)
        self._cb = master.receive
        
    def _handle_message(self, msg):
        self._cb(self, msg)
        
    def disconnect(self, e=None):
        """Disconnect without exiting this process.
        """
        self.logger.debug("disconnect for master channel %s called" % self)
        pass
    
class SerialWorkerChannel(Channel):
    """A very simple channel type used by child processes, that receives incoming
    messages serially, with no task queue.
    """
    
    def __init__(self, *args, **kw):
        super(SerialWorkerChannel, self).__init__(*args, **kw)
    
    def loop(self):
        """Start the polling loop to check for incoming messages, and deliver
        outgoing messages.
        """
        self.logger.debug("%s looping" % self)
        while True:
            self.logger.debug("%s polling" % self)
            active = self._poll.poll()
            for fd, event in active:
                if fd != self._fileno:
                    self.logger.critical("event %s on unkown socket %s (our socket %s)" % (event, fd, self._fileno))
                    continue
                if event & select.POLLHUP:
                    # remote socket has closed connection, we can only read
                    # until the buffer is empty, POLLIN is set anyway so just
                    # log the event
                    self.logger.info("HUP in poll for %s" % self)
                try:
                    if event & select.POLLIN or event | select.POLLPRI:
                        self.read()
                    if event & select.POLLOUT and self._wb:
                        self.write()
                except ChannelDisconnect, e:
                    self.logger.debug("disconnection in loop for %s: %s" % (self, e))
                    self.disconnect()
                    break
                if event & select.POLLERR:
                    self.logger.critical("error on channel %s" % self)
                elif event & select.POLLNVAL:
                    self.disconnect("Error in poll")
                    break
    

class WorkerChannel(Channel):
    """A channel type used by child processes, that queues incoming messages,
    and works on them when there are no new incoming messages. The ordering of
    received messages should be preserved.
    """
    
    def __init__(self, *args, **kw):
        super(WorkerChannel, self).__init__(*args, **kw)
        self._taskq = deque()
        
    def _handle_message(self, msg):
        self._taskq.appendleft(msg)
        
    def loop(self):
        """Start the polling loop to check for incoming messages, deliver
        outgoing messages. Incoming messages are stored in an internal task
        queue, and processed when there is no socket traffic.
        """
        self.logger.debug("%s looping" % self)
        while True:
            self.logger.debug("%s polling" % self)
            if self._taskq:
                active = self._poll.poll(1)
            else:
                active = self._poll.poll()
            for fd, event in active:
                if fd != self._fileno:
                    self.logger.critical("event %s on unkown socket %s (our socket %s)" % (event, fd, self._fileno))
                    continue
                if event & select.POLLHUP:
                    # remote socket has closed connection, we can only read
                    # until the buffer is empty, POLLIN is set anyway so just
                    # log the event
                    self.logger.info("HUP in poll for %s" % self)
                try:
                    if event & select.POLLIN or event | select.POLLPRI:
                        self.read()
                    if event & select.POLLOUT and self._wb:
                        self.write()
                except ChannelDisconnect, e:
                    self.logger.debug("disconnection in loop for %s: %s" % (self, e))
                    self.disconnect()
                    break
                if event & select.POLLERR:
                    self.logger.critical("error on channel %s" % self)
                elif event & select.POLLNVAL:
                    self.disconnect("Error in poll")
                    break
            if self._taskq:
                task = self._taskq.pop()
                if task == 0:
                    # QUIT message, if we have got here the task queue is empty,
                    # if we are not writing we can quit now
                    self.logger.debug("channel %s received a QUIT message" % self)
                    if self._wb:
                        self._quit = True
                    else:
                        self.disconnect()
                try:
                    self.handle_message(task)
                except Exception, e:
                    self.logger.critical("unhandled exception in channel %s: %s" % (self, traceback.format_exc()))
                    self.send(e)
        
class ChattyParallel(object):
    """Start and control child worker processes.
    
    Arguments:
        tasks  -- the list of tasks to send to the child processes
        logger -- a logging Logger instance
    """
    
    def __init__(self, tasks, logger=None):
        self.tasks = tasks
        self._channels = dict()
        self._loads = list()
        self._poll = select.poll()
        self.logger = logger or logging.getLogger('top100.crawler')
        self.pid = os.getpid()
        self.done = 0
    
    def start_channel(self, factory=WorkerChannel):
        """Create a child process, using the given channel factory in the child
        for communication. The factory defaults to the WorkerChannel class. Returns
        the child process id.
        """
        parent, child = socket.socketpair()
        for s in [parent, child]:
            s.setblocking(0)
        pid = os.fork()
        if pid == 0:
            # forked process
            parent.close()
            c = factory(child, pid=self.pid)
            c.loop()
            self.logger.debug("channel %s terminated" % c)
            os._exit(0)
        else:
            child.close()
            channel = MasterChannel(self, parent, poll=self._poll, pid=pid, logger=self.logger)
            self._channels[parent.fileno()] = channel
            self._loads.append((0, channel))
            self.logger.debug("returning channel %s" % channel)
            return pid

    def receive(self, channel, data):
        """Handle incoming messages from child processes."""
        # decrease the load for the receiving channel
        for i, load in enumerate(self._loads):
            if load[1] == channel:
                self.logger.debug("decreasing channel load from %s to %s for channel %s" % (load[0], load[0]-1, channel))
                self._loads[i] = (load[0]-1, channel)
                break
        # increase the number of done messages
        self.done += 1
        # send a new task to the channel
        self._send_task(channel)
        
    def send(self, data, channel=None):
        """Send a message to a child process. If no communication channel is given,
        try to select the least busy child.
        """
        if not self._channels:
            self.logger.critical("send requested without any channels")
            raise ParallelError, "send requested without any channels"
        if not channel:
            # find the least busy channel
            self.logger.debug("finding the least busy channel in %s" % self._loads)
            self._loads.sort()
            load, channel = self._loads[0]
            self._loads[0] = (load+1, channel)
            self.logger.debug("channel %s with load %s selected" % (channel, load))
        else:
            for i, l in enumerate(self._loads):
                if l[1] == channel:
                    self._loads[i] = (l[0]+1, channel)
                    break
        channel.send(data)

    def loop(self, initial_tasks=2):
        """Start the polling loop to check for incoming messages, deliver
        outgoing messages.
        """
        self.logger.debug("sending initial tasks")
        for channel in self._channels.values():
            # prime each channel with a few tasks
            for j in range(initial_tasks):
                self._send_task(channel)
        self.logger.debug("Parallel starting loop")
        while True:
            active = self._poll.poll()
            for fd, event in active:
                channel = self._channels.get(fd)
                if not channel:
                    self.logger.critical("event %s on unkown channel with socket %s" % (event, fd))
                if event & select.POLLHUP:
                    # remote socket has closed connection, we can only read
                    # until the buffer is empty, POLLIN is set anyway so just
                    # log the event
                    self.logger.info("HUP in poll for %s" % self)
                try:
                    if event & select.POLLIN or event | select.POLLPRI:
                        channel.read()
                    if event & select.POLLOUT:
                        channel.write()
                except ChannelDisconnect, e:
                    self.logger.debug("disconnection in loop for %s: %s" % (self, e))
                    self._disconnect(fd)
                if event & select.POLLERR:
                    self.logger.critical("error on channel %s" % channel)
                elif event & select.POLLNVAL:
                    self.logger.critical("disconnect on channel %s" % channel)
                    self._disconnect(fd)
            if len(self._channels) == 0:
                self.logger.debug("Parallel loop terminated")
                break

    def _send_task(self, channel):
        try:
            task = self.tasks.pop()
        except IndexError:
            # we have no more tasks to send
            if not channel.quit_sent:
                # send a QUIT message to the child
                self.logger.debug("sending QUIT message to channel %s" % channel)
                self.send(0, channel)
                channel.quit_sent = True
        else:
            self.send(task)
            
    def _disconnect(self, fd):
        channel = self._channels.get(fd)
        if not channel:
            self.logger.critical("disconnect on fd %s without a channel" % fd)
            self.logger.critical("channels %s" % self._channels)
        else:
            del(self._channels[fd])
        self._poll.unregister(fd)
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
