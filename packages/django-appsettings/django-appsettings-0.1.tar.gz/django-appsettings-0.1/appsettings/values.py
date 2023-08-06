#!/usr/bin/env python

class Value(object):
    def __init__(self, default, doc = ''):
        if not self.validate(default):
            raise ValueError, "invalid default value for type '%s'" % self.__class__.__name__
        self.val = default
        self.doc = doc
        self._parent = None

    def loadVal(self, string):
        '''take a string, parse to actual value'''
        pass

    def serialize(self, val):
        return str(val)

    def validate(self, val):
        '''validate a value'''
        pass

class IntValue(Value):

    def loadVal(self, string):
        self.val = int(string)

    def validate(self, val):
        return type(val) == int

class FloatValue(Value):

    def loadVal(self, string):
        self.val = float(string)

    def validate(self, val):
        return type(val) in (float, int)

class StringValue(Value):

    def loadVal(self, string):
        self.val = string

    def validate(self, val):
        return type(val) is str

class PercentValue(FloatValue):

    def validate(self, val):
        return type(val) in (int, float) and 0 <= val <= 1

class ChoiceValue(Value):

    def __init__(self, options, default, doc = ''):
        self.options = options
        Value.__init__(self, default, doc)

    def loadVal(self, string):
        self.val = string

    def validate(self, val):
        return val in self.options

class BoolValue(Value):

    def loadVal(self, string):
        self.val = string == 'True'

    def validate(self, val):
        return val in (True, False)


# vim: et sw=4 sts=4
