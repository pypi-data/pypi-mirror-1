#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.

"""
Sprained is an integration between U{SpreadModule<http://pypi.python.org/pypi/SpreadModule>},
which is a python interface to U{the spread toolkit<http://spread.org>},
which provides an implementation of virtual synchrony, and U{twisted<http://twistedmatrix.com>},
which provides an asynchronous programming structure.

Please note that sprained has nothing to do with spreadsheets nor does
it have anything to do with the other twisted project with the
unfortunate name of"spread", (which has nothing to do with either
spreadsheets nor virtual synchrony).
"""

__docformat__ = 'epytext'

import os
import copy

from collections import deque

import spread

from zope.interface import implements, Interface

from twisted.internet import reactor
from twisted.internet.interfaces import IReadWriteDescriptor, IReactorFDSet

valid_message_types = set(range(1<<16))
valid_message_reasons = set((spread.CAUSED_BY_JOIN,
                             spread.CAUSED_BY_LEAVE,
                             spread.CAUSED_BY_DISCONNECT,
                             spread.CAUSED_BY_NETWORK,
                             0)) # zero represents transitional membership messages

class ISubscriber(Interface):
    """
    subscribers to L{Mailbox} or L{DispatchingSubscriber} must implement this
    interface.
    """

    def receiveRegular(self, message):
        """
        called when a regular message has been received
        """

    def receiveMembershipChange(self, message):
        """
        called when a membership change message has been received.
        """

class BaseSubscriber(object):
    """
    intended for subclassing, an empty implementation of the L{ISubscriber}
    interface.
    """

    implements(ISubscriber)

    def receiveRegular(self, incoming):
        pass

    def receiveMembershipChange(self, incoming):
        pass

class RegularMsgCopy(object):
    """
    This class stands in for copies of spread.RegularMsgType since
    that type can't be copied or subclassed.
    """
    def __init__(self, message):
        assert isinstance(message, RegularMsgCopy) or isinstance(message, spread.RegularMsgType)

        self.sender = message.sender
        self.groups = message.groups
        self.message = message.message
        self.msg_type = message.msg_type
        self.endian = message.endian

class MembershipMsgCopy(object):
    """
    This class stands in for copies of spread.MembershipMsgType since
    that type can't be copied or subclassed.
    """
    def __init__(self, message):
        assert isinstance(message, MembershipMsgCopy) or isinstance(message, spread.MembershipMsgType)

        self.reason = message.reason
        self.group = message.group
        self.group_id = message.group_id
        self.members = message.members
        self.extra = message.extra

class MsgCopy(object):
    """
    Factory for copying MsgType messages.
    """
    def __new__(cls, message):
        if isinstance(message, spread.RegularMsgType) or isinstance(message, RegularMsgCopy):
            return RegularMsgCopy(message)
        elif isinstance(message, spread.MembershipMsgType) or isinstance(message, MembershipMsgCopy):
            return MembershipMsgCopy(message)
        else:
            raise NotImplementedError, 'Not implemented for class {0}'.format(message.__class__.__name__)

# @ivar queuemax: describes the maximum number of outgoing messages
# we allow in the queue.  We raise QueueOverflow if we hit this.
# @type queuemax: C{int}
queuemax = 409600

class QueueOverflow(Exception):
    """
    raised when L{queuemax} is reached.
    """
    pass

class IRecorder(Interface):
    """
    Base class for recording/playback formats.
    """

    def magic(self):
        """
        return the magic character for this class.
        """

    def encode(self, object):
        """
        Encode an object in the style of pickle.

        @param object:
        @type object: the object to be encoded.

        @return:
        @rtype: encoded C{str} suitable for sending over the wire.
        """
        pass

    def decode(self, input_file):
        """
        Decode an object in the style of pickle.

        @param string:
        @type string: C{str}

        @return:
        @rtype: a reconstructed object.
        """
        pass


class Recorder(object):
    """
    Base instance of IRecorder.  Not intended to be instantiated.
    """
    implements(IRecorder, IReadWriteDescriptor)

    def __init__(self, writer, mailbox, filename):
        assert isinstance(writer, bool)
        self._writer = writer

        assert isinstance(mailbox, Mailbox)
        self._mailbox = mailbox

        assert isinstance(filename, str)
        self._filename = filename
        
        if writer:
            self._outqueue = deque([])
            self._input_file = None

            appending = os.path.exists(self._filename)
            self._fileno = os.open(self._filename, os.O_RDWR | os.O_NONBLOCK | os.O_CREAT)
            if appending:
                magic = os.read(self._fileno, 1)
                assert magic == self.magic(), 'log file = "{0}" lacks magic character {1}'.format(self._filename, self.magic())
                os.lseek(self._fileno, 0, os.SEEK_END) # append to any existing file
            else:
                if os.write(self._fileno, self.magic()) != 1:
                    raise Exception('write failed')
        else:
            pass


    @staticmethod
    def factory(reactor, filename):
        assert isinstance(filename, str)

        fileno = os.open(filename, os.O_RDONLY | os.O_NONBLOCK)
        magic = os.read(fileno, 1)
        if magic == JSON.magic():
            c = JSON
        elif magic == Pickle.magic():
            c = Pickle
        else:
            raise NotImplementedError, 'Not implemented for magic = "{0}"'.format(magic)

        playbacker = c(False, reactor, filename)
        playbacker._fileno = fileno
        playbacker._input_file = fdopen(playbacker._fileno, 'rb')
        reactor.addReader(playbacker)
        

    def magic(self):
        raise NotImplementedError, 'magic() not implemented for {0}'.format(self.__class__.__name__)

    def encode(self, object):
        raise NotImplementedError, 'encode() not implemented for {0}'.format(self.__class__.__name__)

    def decode(self, inputfile):
        raise NotImplementedError, 'decode() not implemented for {0}'.format(self.__class__.__name__)

    def fileno(self):
        return self._fileno

    def write(self, message):
        if len(self._outqueue) >= queuemax:
            raise QueueOverflow

        assert(len(self._outqueue) < queuemax)

        if not self._outqueue:
            self._mailbox._reactor.addWriter(self)

        self._outqueue.append(message)

    def doWrite(self):
        message = MsgCopy(self._outqueue.popleft())

        if isinstance(message, RegularMsgCopy):
            if message.sender == self._mailbox.private_group():
                message.sender = None

            grouplist = list(message.groups)
            while self._mailbox.private_group() in grouplist:
                grouplist[grouplist.index(self._mailbox.private_group())] = None
            message.groups = tuple(grouplist)

        elif isinstance(message, MembershipMsgCopy):
            while self._mailbox.private_group() in message.members:
                message.members[message.members.index(None)] = None

            while self._mailbox.private_group() in message.extra:
                message.extra[message.extra.index(None)] = None

        else:
            raise NotImplementedError, 'unrecognized type {0}'.format(message.__class__.__name__)

        encoded = self.encode(message)
        bytes_sent = os.write(self._fileno, encoded)

        if bytes_sent != len(encoded):
            raise Exception('bad write {0}/{1}'.format(bytes_sent, len(encoded)))

        if not self._outqueue:
            self._reactor.removeWriter(self)

        return None

    def connectionLost(self, whatever):
        if self._input_file:
            self._input_file.close()
        else:
            os.close(self._fileno)

    def logPrefix(self):
        return self.__class__.__name__

    def doRead(self):
        message = self.decode(self._input_file)

        if isinstance(message, RegularMsgCopy):
            if message.sender == None:
                message.sender = message._mailbox.private_group()

            while None in message.groups:
                message.groups[message.groups.index(None)] = message._mailbox.private_group()

        elif isinstance(message, MembershipMsgCopy):
            while None in message.members:
                message.members[message.members.index(None)] = message._mailbox.private_group()

            while None in message.extra:
                message.extra[message.extra.index(None)] = message._mailbox.private_group()
 
        else:
            raise NotImplementedError, 'unrecognized type {0}'.format(message.__class__.__name__)

        self._mailbox._dispatch(message)

class JSON(Recorder):
    """
    Class representing standard JSON library recording/playback formats.
    """

    import json

    @staticmethod
    def magic():
        return 'a'

    @staticmethod
    def encode(object):
        return json.dumps(object, sort_keys=True, indent=4)

    @staticmethod
    def decode(input_file):
        return json.load(input_file)


class Pickle(Recorder):
    """
    Class representing standard pickle library recording/playback formats.
    """

    try:
        import cPickle as pickle
    except ImportError:
        import pickle

    @staticmethod
    def magic():
        return 'b'

    @staticmethod
    def encode(object):
        return pickle.dumps(object)

    @staticmethod
    def decode(input_file):
        return pickle.load(input_file)


import yaml
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class YAML(Recorder):
    """
    Class representing YAML library recording/playback formats.
    """

    @staticmethod
    def magic():
        return 'c'

    @staticmethod
    def encode(object):
        return yaml.dump(object, Dumper=Dumper)

    @staticmethod
    def decode(input_file):
        return yaml.load(input_file, Loader=Loader)


class Mailbox(object):
    """
    U{Twisted<http://twistedmatrix.com>} calls this a factory, except
    that factories listen on a socket and spawn new instances of
    protocols.
    U{SpreadModule<http://pypi.python.org/pypi/SpreadModule>} calls it
    a U{spread.MailboxType}, which is closer to relevant for Sprained.

    This object corresponds to a single connection to a spread server.
    It's primary job is to manage that connection which includes
    making it, breaking it, sending outgoing messages, and dispatching
    incoming messages on to the appropriate subscribers, (which are
    somewhat analogous to twisted's protocols).

    @ivar _reactor:
    @type _reactor: an object which implements L{twisted.internet.interfaces.IReactorFDSet}

    @ivar _spread_name:
    @type _spread_name: see L{__init__}

    @ivar _priority:
    @type _priority: see L{__init__}

    @ivar _membership:
    @type _membership: see L{__init__}

    @ivar _groups:
    @type _groups: a C{dict} of L{ISubscriber} by C{str} group name to which this object is listening.

    @ivar _outqueue:
    @type _outqueue: a C{collection.deque} of C{str} messages waiting to be sent.

    @ivar _mb:
    @type _mb: the underlying L{spread.MailboxType} for this connection.
    """

    implements(IReadWriteDescriptor)

    def __init__(self,
                 myreactor=reactor,
                 spread_name='{0}'.format(spread.DEFAULT_SPREAD_PORT),
                 private_name='',
                 priority=0,
                 membership=True,
                 record='',
                 recorder=YAML,
                 playback=''
                 ):
        """
        Some of these derive directly from L{SpreadModule}.

        Currently known formats for recording/playback to/from a log file are:

        - L{Mailbox.RecordingFormat.Pickle} for the use of the python standard L{pickle} module.
        - L{Mailbox.RecordingFormat.JSON} for the use of the python standard L{json} module.

        @param myreactor:
        @type myreactor: an object which implements L{twisted.internet.interfaces.IReactorFDSet}

        @param spread_name:
        @type spread_name: a C{str} specifying the port and host of
        the spread daemon to use, of the form"<port>@<hostname>" or
        "<port>", where <port> is an integer port number (typically the constant
        DEFAULT_SPREAD_PORT) represented as a string, and <hostname> specifies
        the host where the daemon runs, typically"localhost".  The default is the
        default Spread port and host.

        @param private_name:
        @type private_name: a string specifying the name under which this client is to be
        known; the default is a private name made up by Spread

        @param priority:
        @type priority: C{int} - 0 or 1, currently unused; default 0

        @param membership:
        @type membership: C{bool} - if true, then request receipt of membership change messages.

        @param record: when this is set, it is expected to be a valid
        file name.  All incoming messages are both dispatched as usual
        as well as being appended to this log file.  The file is
        created if it does not exist.

        @type record: C{str}

        @param recorder: represents the format we will use for recording.  This is ignored if L{record} is not set.
        @type recorder: L{Recorder}

        @param playback: when this is set, it is expected to be a
        valid, existing file name.  Instead of reading messages from
        the network as usual, messages are read from this file and
        then dispatched.
 
        @type playback: C{str}
        """

        assert IReactorFDSet.providedBy(myreactor)
        self._reactor = myreactor

        assert isinstance(spread_name, str)
        self._spread_name = spread_name

        assert isinstance(private_name, str)

        assert isinstance(priority, int)
        self._priority = priority

        assert isinstance(membership, bool)
        if membership:
            self._membership = 1
        else:
            self._membership = 0

        self._groups = {}
        self._outqueue = deque([])

        assert isinstance(record, str)
        self._record = record

        self._mb = spread.connect(self._spread_name, private_name, self._priority, self._membership)

        if self._record:
            assert issubclass(recorder, Recorder)
            self._recorder = recorder(True, self, self._record)

        assert isinstance(playback, str)
        self._playback = playback

        if self._playback:
            self._playbacker = Recorder.factory(self._playback)
        else:
            self._reactor.addReader(self)


    def fileno(self):
        """
        return the file descriptor of the underlying L{spread.MailboxType}
        """
        return self._mb.fileno()

    def private_group(self):
        """
        return the the private group name assigned to this connection by the spread
        daemon (see the SP_connect man page).
        """
        return self._mb.private_group

    def connectionLost(self, exception):
        """
        called by the reactor when it is time to relinquish a connection.
        """
        self._mb.disconnect()
        self._reactor.removeReader(self)

        if self._membership:
            # FIXME: probably need to wait for disconnect message
            pass

    def logPrefix(self):
        """
        a requirement for implementing L{IReadWriteDescriptor}.  I'm not
        sure when it's used.
        """
        return self.__class__.__name__

    def doRead(self):
        """
        called from the reactor when our file descriptor is readable.
        """
        incoming = self._mb.receive()

        # copy it immediately.  This allows others to copy easily
        # later and potentially to subclass.
        incoming = MsgCopy(incoming)

        if self._record:
            self._recorder.write(incoming)

        self._dispatch(incoming)


    def _dispatch(self, incoming):
        """
        dispatch a message.
        """

        if isinstance(incoming, RegularMsgCopy):
            for group in incoming.groups:
                for subscriber in self._groups[group].copy():
                    subscriber.receiveRegular(incoming)
        elif isinstance(incoming, MembershipMsgCopy):
            if incoming.group in self._groups:
                for subscriber in self._groups[incoming.group].copy():
                    subscriber.receiveMembershipChange(incoming)
        else:
            raise Exception('unrecognized message type')


    def multicast(self, service, groups, outgoing='', msg_type=0):
        """
        send a message.

        @param service:
        @type service: one of the integer constants (see the SP_multicast man
        page for their meaning): L{spread.UNRELIABLE_MESS},
        L{spread.RELIABLE_MESS}, L{spread.FIFO_MESS}, L{spread.CAUSAL_MESS},
        L{spread.AGREED_MESS}, L{spread.SAFE_MESS}.

        @param groups:
        @type groups: a C{tuple} of C{str} of group names.

        @param outgoing: the outgoing message.
        @type outgoing: C{str}

        @param msg_type:
        @type msg_type: C{int} (must be 16-bit int)
        """
        
        self.validateGroups(groups)
        if len(self._outqueue) >= queuemax:
            raise QueueOverflow
        assert(len(self._outqueue) < queuemax)

        if not self._outqueue:
            self._reactor.addWriter(self)

        self._outqueue.append((service, groups, outgoing, msg_type))

    def doWrite(self):
        """
        called from the reactor when our file descriptor is writable and we've
        been asked to be notified of that fact.
        """
        q = self._outqueue.popleft()
        self._mb.multigroup_multicast(*q)

        if not self._outqueue:
            self._reactor.removeWriter(self)

        return None

    @staticmethod
    def validateGroups(groups):
        """
        validate a tuple of groups using assert
        """
        assert(isinstance(groups, tuple))
        for g in groups:
            assert(isinstance(g, str))

    def subscribe(self, groups, subscriber):
        """
        add an object which implements L{ISubscriber} to the C{set} of objects
        which will be called on receipt of messages on the specified groups.

        @param groups:
        @type groups: a C{tuple} of C{str} group names.

        @param subscriber:
        @type subscriber: an object which implements L{ISubscriber}.
        """

        self.validateGroups(groups)
        assert ISubscriber.providedBy(subscriber)

        for group in groups:
            suppressjoin = False
            if group in self._groups:
                suppressjoin = [s for s in self._groups[group]
                                if not isinstance(s, self._LastHurrah)]
                
                self._groups[group] |= set([subscriber])
            else:
                self._groups[group] = set([subscriber])

            if ((not suppressjoin)
                and (group != self._mb.private_group)):
                self._mb.join(group)

    class _LastHurrah(BaseSubscriber):
        """
        spread returns the membership change message for departures after the
        part has occurred.  In order to deliver this final message, we need to
        delay a little.  _LastHurrah's job is to catch such messages, forward it
        on, and then remove itself from the subscription list.
        """

        implements(ISubscriber)

        def __init__(self, mb, group, subscriber):
            """
            @param mb:
            @type mb: an object of type L{Mailbox}

            @param group:
            @type group: C{str} name of the group we're representing.

            @param subscriber:
            @type subscriber: object which implements L{ISubscriber} to which
            we will forward the final message.
            """
            self._mb = mb
            self.group = group
            self.subscriber = subscriber

        def receiveMembershipChange(self, incoming):
            """
            final message catcher
            """
            assert isinstance(incoming, MembershipMsgCopy)

            # if it's us, deliver and unsubscribe
            if ((incoming.reason == spread.CAUSED_BY_LEAVE)
                and (incoming.group == self.group)):
                self.subscriber.receiveMembershipChange(incoming)
                self._mb.unsubscribe((self.group,), self)

    def unsubscribe(self, groups, subscriber):
        """
        remove a subscriber from the set of objects to receive messages on the
        specified groups.

        @param groups:
        @type groups: a C{tuple} of C{str} group names.

        @param subscriber:
        @type subscriber: an object which implements L{ISubscriber}.
        """
        self.validateGroups(groups)

        for group in groups:
            self._groups[group] -= set([subscriber])
            if not self._groups[group]:
                if group != self._mb.private_group:
                    if not isinstance(subscriber, self._LastHurrah):
                        self.subscribe((group,), self._LastHurrah(self, group, subscriber))
                    self._mb.leave(group)
                else:
                    del self._groups[group]

    def private_name(self):
        return self._mb.private_name


class DispatchingSubscriber(BaseSubscriber):
    """
    This object represents a conventional L{Mailbox} subscriber.  It
    dispatches messages received on specific groups on the basis of
    L{RegularMsgCopy.msg_type} or L{MembershipMsgCopy.reason}.

    @ivar _mailbox:
    @type _mailbox: L{Mailbox}

    @ivar _regularCallbacks:
    @type _regularCallbacks: a C{dict} of C{set} by callback where the
    C{set} describes the L{RegularMsgCopy.msg_type}s of interest.

    @ivar _membershipCallbacks:
    @type _membershipCallbacks: a C{dict} of C{set} by callback where the
    C{set} describes the L{MembershipMsgCopy.reasons}s of interest.
    """

    implements(ISubscriber)

    # LATER: it might be more efficient here to keep a list of
    # (ranges, [callback, callback]) but it would also be more work.

    def __init__(self, mailbox, groups):
        """
        @param mailbox:
        @type mailbox: L{Mailbox}

        @param groups:
        @type groups: a C{tuple} of C{str} of group names.
        """

        assert isinstance(mailbox, Mailbox)
        self._mailbox = mailbox

        self._mailbox.validateGroups(groups)
        self._groups = groups

        self._regularCallbacks = []
        self._membershipCallbacks = []

        # LATER: might want to add supersets here so we can quickly
        # tell if we have anything to dispatch.

        self._mailbox.subscribe(groups, self)

    def rm(self):
        self._mailbox.unsubscribe(self._groups, self)
    
    def _validate(self):
        """
        Validate everything we can about this object.  Intended for
        debugging and development, not production use.
        """
        assert isinstance(self._mailbox, Mailbox)
        self._mailbox.validateGroups(self._groups)

        assert isinstance(self._regularCallbacks, list)
        for (key, types) in self._regularCallbacks:
            assert isinstance(types, set)
            assert types <= valid_message_types
            (callback, args, kwargs) = key
            assert callable(callback)
            assert isinstance(args, tuple)
            assert isinstance(dict, kwargs)

        assert isinstance(self._membershipCallbacks, list)
        for (key, types) in self._membershipCallbacks:
            assert isinstance(types, set)
            assert types <= valid_message_reasons
            (callback, args, kwargs) = key
            assert callable(callback)
            assert isinstance(args, tuple)
            assert isinstance(dict, kwargs)

    def _validateKey(self, key):
        assert isinstance(key, tuple)
        assert len(key) is 3
        (callback, args, kwargs) = key
        assert callable(callback)
        assert isinstance(args, tuple)
        assert isinstance(kwargs, dict)

    def _find(self, target_list, target_key):
        """
        Search the list for an entry that matches key.  Return the entry or None.
        
        @param target_list:
        @type target_list: either L{self._regularCallbacks} or L{self._membershipCallbacks}.

        @param target_key:
        @type target_key: a C{tuple} of (callback, args, kwargs).
        """
        assert (target_list is self._regularCallbacks) or (target_list is self._membershipCallbacks)
        self._validateKey(target_key)

        for i in target_list:
            (key, values) = i
            if key == target_key:
                return i
        return None

    def _register(self, registry, callback, domain, args, kwargs):
        assert (registry is self._regularCallbacks) or (registry is self._membershipCallbacks)
        assert callable(callback)
        assert isinstance(domain, set)

        key = (callback, args, kwargs)
        entry = self._find(registry, key)
        if entry:
            (key, types) = entry
            types |= domain
        else:
            registry.append((key, domain.copy()))


    def _unregister(self, registry, callback, domain, args, kwargs):
        assert (registry is self._regularCallbacks) or (registry is self._membershipCallbacks)
        assert callable(callback)
        assert isinstance(domain, set)

        key = (callback, args, kwargs)
        entry = self._find(registry, key)
        if entry:
            (key, types) = entry
            types -= domain
            if not types:
                registry.remove(entry)
        

    def registerRegular(self, callback, msg_range, *args, **kwargs):
        """
        Add a callback to the set of callbacks which will be called on
        receipt of L{RegularMsgCopy}s on our groups with
        L{RegularMsgCopy.msg_type}s in the specified msg_range.

        Arguments are the same as for L{unregisterRegular}.

        @param callback:
        @type callback: callable object with args (message, ...)

        @param msg_range:
        @type msg_range: either a C{2-tuple} of the low and high message type
        numbers, (inclusive), or a C{set} of L{RegularMsgCopy.msg_type}s.
        """
        assert callable(callback)
        assert isinstance(msg_range, (set, tuple))

        if isinstance(msg_range, tuple):
            msg_range = set(xrange(msg_range[0], msg_range[1] + 1))

        self._register(self._regularCallbacks, callback, msg_range, args, kwargs)

    def unregisterRegular(self, callback, msg_range, *args, **kwargs):
        """
        Remove a callback from the list of callbacks which will be
        called on receipt of L{RegularMsgCopy}s on our groups
        with L{RegularMsgCopy.msg_type}s in the msg_range.

        Arguments are the same as for L{enrollRegular}.

        @param callback:
        @type callback: callable object with args (message, ...)

        @param msg_range:
        @type msg_range: C{set} of L{RegularMsgCopy.msg_type}s.
        """
        assert callable(callback)
        assert isinstance(msg_range, (set, tuple))

        if isinstance(msg_range, tuple):
            msg_range = set(xrange(msg_range[0], msg_range[1] + 1))

        self._unregister(self._regularCallbacks, callback, msg_range, args, kwargs)

    def receiveRegular(self, message):
        """
        called by L{Mailbox} when our group receives a L{RegularMsgCopy}.
        """
        assert isinstance(message, RegularMsgCopy)
        for entry in self._regularCallbacks[:]:
            (key, types) = entry
            if message.msg_type in types:
                (callback, args, kwargs) = key
                callback(message, *args, **kwargs)

    def registerMembership(self, callback, reasons, *args, **kwargs):
        """
        Add a callback to the list of callbacks which will be called
        on receipt of L{MembershipMsgCopy}s on our groups with
        L{MembershipMsgCopy.reason}s in the specified set of
        reasons.

        Arguments are the same as for L{unregisterMembership}.

        @param callback:
        @type callback: callable object with args (message, ...)

        @param reasons:
        @type reasons: a C{set} of L{MembershipMsgCopy.reason}s.
        """
        assert callable(callback)
        assert isinstance(reasons, set)

        self._register(self._membershipCallbacks, callback, reasons, args, kwargs)


    def unregisterMembership(self, callback, reasons, *args, **kwargs):
        """
        Remove a callback from the list of callbacks which will be
        called on receipt of L{MembershipMsgCopy}s on our
        groups for the specified L{MembershipMsgCopy.reason}s.

        Arguments are the same as for L{registerMembership}.

        @param callback:
        @type callback: callable object with args (message, ...)

        @param reasons:
        @type reasons: C{set} of L{MembershipMsgCopy.reason}s.
        """
        assert callable(callback)
        assert isinstance(reasons, set)

        self._unregister(self._membershipCallbacks, callback, reasons, args, kwargs)

    def receiveMembershipChange(self, message):
        """
        called by L{Mailbox} when our group receives a L{MembershipMsgCopy}.
        """
        assert isinstance(message, MembershipMsgCopy)
        for entry in self._membershipCallbacks[:]:
            (key, types) = entry
            if message.reason in types:
                (callback, args, kwargs) = key
                callack(message, *args, **kwargs)

    def multicast(self, service, outgoing='', msg_type=0):
        """
        send a message to our groups

        @param service:
        @type service: one of the integer constants (see the SP_multicast man
        page for their meaning): L{spread.UNRELIABLE_MESS},
        L{spread.RELIABLE_MESS}, L{spread.FIFO_MESS}, L{spread.CAUSAL_MESS},
        L{spread.AGREED_MESS}, L{spread.SAFE_MESS}.

        @param outgoing: the outgoing message.
        @type outgoing: C{str}

        @param msg_type:
        @type msg_type: C{int} (must be 16-bit int)
        """
        self._mailbox.multicast(service, self._groups, outgoing, msg_type)

    def private_group(self):
        """
        Return the private group associated with this object.
        """
        return self._mailbox.private_group()
