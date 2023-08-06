#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The Purity library for Pure Data dynamic patching.
#
# Copyright 2009 Alexandre Quessy
# <alexandre@quessy.net>
# http://alexandre.quessy.net
#
# Purity is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Purity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the gnu general public license
# along with Purity.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Tools to create Pure Data objects and subpatches.

This is meant to be used by any network library. The FUDI protocol 
is in a separate module and is not used here. 

See the client module for an implementation of this using the FUDI 
protocol for Twisted.

One could write a non-asynchronous version of this. (no network here)
"""
#TODO: rename this file to patch.py
import random 
from zope import interface

VERBOSE = True
VERY_VERBOSE = False

_gen_pos_indexes = {}

def _gen_position(parent, be_random=False):
    """
    Generates positions for an object within a parent patch.
    Keeps track of the previous object Y position using 
    the memory address of the parent object as a key in the dict.
    """
    global _gen_pos_indexes
    parent_id = id(parent)
    increment = 25 # distance between objects in the patches.
    if parent_id not in _gen_pos_indexes.keys():
        _gen_pos_indexes[parent_id] = 0 # start at 0
    if be_random:
        return [random.randrange(10, 300), random.randrange(10, 200)]
    else:
        _gen_pos_indexes[parent_id] += increment # and then increment
        return [100, _gen_pos_indexes[parent_id]] # object pos
    
class IElement(interface.Interface):
    """
    Any Pure Data Element. (object or message)
    """
    parent = interface.Attribute("""A pointer to the parent Element.""")

    def get_fudi(self):
        """
        Returns a (Python) list of lists of (python-typed) atoms, or just a 
        list of python-typed atoms. 
        
        What I mean by "python-typed" is the built-in python types, such as
        int, str, float, bool. 
        
        It returns the FUDI message needed to create the element, and
        maybe its sub-elements. A FUDI creation message.
        
        If it is a SubPatch, it returns a list of lists. (2D)
        Elements such as Obj and Msg return a one-dimension list. (1D)

        That list must then be converted to real ASCII fudi using the 
        fudi module.
        """
        pass

    def set_parent(self, obj):
        """
        Sets the parent. 
        :param obj: An Element.
        """
        pass

class Obj(object):
    """
    Generic Pure Data Object.
    """
    interface.implements(IElement)
    def __init__(self, name, *args, **keywords):
        """
        Keywords: pos, x, y
        """
        self.parent = None
        self.name = name
        self.args = args
        self.pos = [0, 0] # _gen_position(self.parent) # [random.randrange(10, 600), random.randrange(10, 400)]
        if keywords.has_key("pos"):
            self.pos = keywords["pos"]
        if keywords.has_key("x"):
            self.pos[0] = keywords["x"]
        if keywords.has_key("y"):
            self.pos[1] = keywords["y"]

    def get_fudi(self):
        """
        Returns a list of (python-typed) atoms.
        """
        li = ["obj", self.pos[0], self.pos[1], self.name]
        li.extend(self.args)
        return li
    
    def set_parent(self, obj):
        self.parent = obj

    def set_position(self, x, y):
        self.pos = [x, y]

class Msg(object):
    """
    Pure Data message box.
    """
    # TODO: escape characters such as ","
    interface.implements(IElement)
    def __init__(self, *args, **keywords):
        """
        Keywords: pos, x, y
        """
        self.parent = None
        self.args = args
        self.pos = [0, 0]
        if keywords.has_key("pos"):
            self.pos = keywords["pos"]
        if keywords.has_key("x"):
            self.pos[0] = keywords["x"]
        if keywords.has_key("y"):
            self.pos[1] = keywords["y"]

    def get_fudi(self):
        """
        Returns a list of (python-typed) atoms.
        """
        li = ["msg", self.pos[0], self.pos[1]]
        li.extend(self.args)
        return li
    
    def set_parent(self, obj):
        self.parent = obj

    def set_position(self, x, y):
        self.pos = [x, y]

class Receive(Obj):
    """
    The [receive] Pure Data object.
    It has a send method, which you can be used to send it a message
    directly.
    """
    def __init__(self, receive_symbol):
        self.receive_symbol = receive_symbol
        self.purity_client = None
        Obj.__init__(self, "r", receive_symbol)

    def set_client(self, purity_client):
        self.purity_client = purity_client

    def send(self, *args):
        """
        Returns a FUDI message suitable to be sent to that [receive] object. 
        """
        li = [self.receive_symbol]
        li.extend(args)
        if self.purity_client is not None:
            self.purity_client.send_message(self.receive_symbol, *args)
        return li

class Connection(object):
    """
    Connection between two Pure Data objects.
    """
    interface.implements(IElement)
    def __init__(self, from_object, from_outlet, to_object, to_inlet):
        self.parent = None
        self.from_object = from_object
        self.from_outlet = from_outlet
        self.to_object = to_object
        self.to_inlet = to_inlet
        # self.subpatch_name = "default"

    def get_fudi(self):
        """
        Returns fudi creation list.
        """
        # self.subpatch_name, 
        return ["connect", self.from_object.id, self.from_outlet, self.to_object.id, self.to_inlet]

    def set_parent(self, obj):
        self.parent = obj

class SubPatch(object):
    """
    Pure Data Subpatch. 
    
    The default name is "__main__" for the [pd __main__] subpatch.
    It can be found in purepy/data/dynamic_patch.pd
    """
    #TODO: add msg method.
    #TODO: allow to connect message boxes
    interface.implements(IElement)
    def __init__(self, name="__main__", visible=False):
        self.parent = None
        self.name = name
        self.visible = visible
        self.objects = []
        self.connections = []
        # self.pos = [0, 0]
        self.pos = _gen_position(self)
    
    def set_parent(self, obj):
        self.parent = obj
    
    def get_fudi(self):
        """
        Return FUDI lists for the whole subpatch.
        Objects and connections
        """
        result = []
        if self.name != "__main__":
            # TODO: random position... 
            # pos = _gen_position(self)
            pos = self.pos
            l = ["pd-%s" % (self.parent.name), "obj", pos[0], pos[1], "pd", self.name]
            result.append(l)
        if VERY_VERBOSE:
            print "objects"
        for obj in self.objects: 
            # obj.pos = # _gen_position(self)
            if type(obj) is SubPatch: # subpatch
                result.extend(obj.get_fudi())
            else: # standard obj
                l = ["pd-%s" % (self.name)]
                l.extend(obj.get_fudi())
                result.append(l)
                if VERY_VERBOSE:
                    print l
        if VERY_VERBOSE:
            print "connections"
        for conn in self.connections:
            l = ["pd-%s" % (self.name)]
            l.extend(conn.get_fudi())
            result.append(l)
            if VERY_VERBOSE:
                print l
        if not self.visible:
            l = ["pd-%s" % (self.name), "vis", 0]
            result.append(l)
            if VERY_VERBOSE:
                print l
        if VERY_VERBOSE:
            print "done creating FUDI list"
        return result

    def subpatch(self, name, visible=False):
        """
        Adds a subpatch to the supatch.
        Factory that wraps the SubPatch constructor.
        @return SubPatch instance.
        """
        obj = SubPatch(name, visible=visible)
        return self._add_object(obj)

    def obj(self, name, *args, **keywords):
        """
        Adds an object to the supatch.
        Factory that wraps the Obj constructor.
        @return Obj instance.
        """
        obj = Obj(name, *args, **keywords)
        return self._add_object(obj)

    def msg(self, *args, **keywords):
        """
        Adds an message box to the supatch.
        Factory that wraps the Msg constructor.
        @return Msg instance.
        """
        # we just put it in the self.objects list for convenience
        msg = Msg(*args, **keywords)
        return self._add_object(msg)

    def _add_object(self, obj):
        """
        Common to self.obj(), self.subpatch() and self.receive(). 
        """
        obj.id = len(self.objects)
        pos = _gen_position(self) # this is where position is decided.
        obj.set_parent(self)
        obj.set_position(*pos)
        self.objects.append(obj)
        return obj
        
    def set_position(self, x, y):
        self.pos = [x, y]

    def receive(self, receive_symbol):
        """
        Similar to obj(), but for a receive object only.
        Appends a [receive] object to the subpatch.
        """
        obj = Receive(receive_symbol)
        return self._add_object(obj)
    
    def connect(self, from_object, from_outlet, to_object, to_inlet):
        """
        Connects two objects together.
        Returns None
        """
        if from_object not in self.objects:
            raise PureError("%s object not in subpatch %s" % (from_object, self))
        elif to_object not in self.objects:
            raise PureError("%s object not in subpatch %s" % (to_object, self))
        else:
            conn = Connection(from_object, from_outlet, to_object, to_inlet)
            self.connections.append(conn)
            # conn.subpatch_name = self.name
            
    def clear(self):
        """
        Returns a message to clear the subpatch.
        """
        # TODO: send it directly
        self.connections = []
        self.objects = []
        return ["pd-%s" % (self.name), "clear"]

def get_main_patch():
    """
    Returns a sub patch which is [pd main] in the dynamic_patch.pd patch.
    """
    #TODO: rename to [pd __main__]
    return SubPatch() # default arg is that one

if __name__ == "__main__":
    from purity import fudi
    def test_1(main):
        # subpatch
        test1 = main.subpatch("test1")
        # objects
        r = test1.receive("startme")
        tgl = test1.obj("tgl")
        metro = test1.obj("metro", 50)
        # connections
        test1.connect(r, 0, tgl, 0)
        test1.connect(tgl, 0, metro, 0)

    main = SubPatch()
    for test in [test_1]:
        test(main)
    print("------ test results ------")
    li = main.get_fudi() 
    for i in li:
        if len(i) == 0:
            print(fudi.to_fudi(i[0]).strip())
        else:
            print(fudi.to_fudi(i[0], *i[1:]).strip())




