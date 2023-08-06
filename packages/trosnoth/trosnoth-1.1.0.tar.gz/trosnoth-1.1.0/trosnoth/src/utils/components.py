# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from trosnoth.src.utils import logging

class Component(object):
    def __init__(self):
        # Find all the plugs.
        plugs = {}
        plugsByName = {}
        for k in dir(self):
            v = getattr(self, k)
            if isinstance(v, Plug):
                plugs[v] = plugsByName[k] = BoundPlug(v, self)

        # Go through methods and check for handlers.
        for k in dir(self):
            v = getattr(self, k)
            if isinstance(v, Handler):
                for message, plug in v.bits:
                    if plug is None:
                        # Handles messages from all plugs.
                        for p in plugs.itervalues():
                            if message in p._methods:
                                raise KeyError('handler already defined for %s/%s' % (p, message))
                            p._methods[message] = v.method
                    else:
                        # Handles messages from one plug only.
                        p = plugs[plug]
                        if message in p._methods:
                            raise KeyError('handler already defined for %s/%s' % (p, message))
                        p._methods[message] = v.method

        for k, v in plugsByName.iteritems():
            setattr(self, k, v)
                
class UnboundPlug(object):
    '''
    This is called UnboundPlug so that error messages make it clear that this
    plug is unbound. Plug is an alias for UnboundPlug in order to make more
    sense in written code.
    '''
Plug = UnboundPlug

def queueMessage(target, message):
    # Note: it may be sensible to use a callLater here instead.
    try:
        target._receive(message)
    except:
        logging.writeException()

class UnhandledMessage(Exception):
    pass

class BoundPlug(object):
    def __init__(self, plug, obj):
        self.plug = plug
        self.obj = obj
        self.targets = []
        self._methods = {}

    def send(self, message):
        for target in self.targets:
            queueMessage(target, message)

    def _receive(self, message):
        # Find the correct handler.
        try:
            method = self._methods[type(message)]
        except KeyError:
            print self._methods
            raise UnhandledMessage('%s does not handle %s' % (self.obj, message))

        # Call this handler.
        method(self.obj, message)

    def connectPlug(self, plug):
        '''
        Note that this unplugs the current plug and plugs it into the remote
        plug without unplugging the remote plug from anything it's plugged
        into.
        '''
        for other in self.targets:
            self.disconnectPlug(other)

        self.targets = [plug]
        plug.targets.append(self)

    def disconnectAll(self):
        '''
        Disconnects this plug from everything it's attached to.
        '''
        for other in self.targets:
            self.disconnectPlug(other)

    def disconnectPlug(self, plug):
        '''
        Unplugs a connection between this plug and the given plug if such a
        connection exists.
        '''
        try:
            self.targets.remove(plug)
        except KeyError:
            pass

        try:
            plug.targets.remove(self)
        except KeyError:
            pass

class MessageClass(type):
    '''
    This metaclass is provided for convenience. It checks if you have provided
    a single string for the .fields class attribute and if so converts it to a
    tuple.
    '''
    def __new__(cls, name, bases, dictn):
        # Test for a single string cls.fields and make tuple.
        if isinstance(dictn.get('fields'), str):
            dictn['fields'] = (dictn['fields'],)

        # Do the real building.
        return type.__new__(cls, name, bases, dictn)

class MessageBase(object):
    '''
    Allows message classes to be defined by:
        class CustomMessage(Message):
            fields = ('myField', 'otherField')
    And then instantiated by:
        x = CustomMessage(17, otherField=2)
    Which will create an object where:
        x.myField == 17
        x.otherField == 2
    '''

    def __init__(self, *args, **kwargs):
        if len(args) > len(self.fields):
            raise TypeError('%s takes at most %d arguments (%d given)' % 
                    (type(self), len(self.fields), len(args)))

        # Simply get the args and store them as attributes of self.
        for i in xrange(len(args)):
            k = self.fields[i]
            v = args[i]
            if k in kwargs:
                raise TypeError('got multiple values for keyword argument %r' % (k,))
            kwargs[k] = v

        for k,v in kwargs.iteritems():
            setattr(self, k, v)

    def __repr__(self):
        args = []
        for k in self.fields:
            args.append(repr(getattr(self, k)))
        return '%s(%s)' % (type(self).__name__, ', '.join(args))

class Message(MessageBase):
    __metaclass__ = MessageClass
        
class Handler(object):
    def __init__(self, method, message, plug=None):
        self.method = method
        if plug is not None and not isinstance(plug, UnboundPlug):
            raise TypeError('plug must be UnboundPlug, not %s' % (plug,))
        self.bits = [(message, plug)]

def handler(message, plug=None):
    def handler(method):
        if isinstance(method, Handler):
            method.bits.append((message, plug))
            return method
        return Handler(method, message, plug)
    return handler
