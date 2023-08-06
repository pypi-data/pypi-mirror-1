# Copyright 2007-2009 Nathan Davis

# This file is part of PyMultimethods
#
# PyMultimethods is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyMultimethods is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyMultimethods.  If not, see <http://www.gnu.org/licenses/>.

from types import FunctionType, ClassType, TypeType, MethodType

def _mro(cls):
    """
    A primitive "multimethod" for obtaining the mro of a class
    
    Returns an iterator over the mro of the input cls
    """
    if isinstance(cls, TypeType):
        for base in cls.mro():
            yield base
    else:
        yield cls
        for base in cls.__bases__:
            for c in _mro(base):
                yield c
    
    #Everything is anything, the ultimate catch-all
    yield anything

def _isinstance(obj, cls):
    """
    A primitive "multimethod" for determining whether obj is an instance of cls.
    This differs from the built-in implemention in it handles the case where cls is a not a type (i.e., it's a ClassID instance).
    
    Returns True iff obj is an instance of cls
    """
    if isinstance(cls, type) or isinstance(cls, ClassType):
        return isinstance(obj, cls)
    else:
        if hasattr(obj, "CLASS_ID"):
            if obj.CLASS_ID == cls:
                return True
            for c in _mro(obj.__class__):
                if hasattr(c, "CLASS_ID") and c.CLASS_ID == cls:
                    return True
    return False

class ClassID(object): pass
class anything:
    """
    catch-all type-specifier that matches all types (including all old-style classes)
    """

class Rule(object):
    def __init__(self):
        self.next = MultiMethod()
        self.defaultable = False
    
    #You can uncomment this function if you need to do debugging.
    #def __repr__(self):
        #return str((self.next, self.defaultable))

class MultiMethod(object):
    def __init__(self):
        """Creates a MultiMethod object. initially with no rules."""
        self.by_value = dict() #value -> Rule
        self.rules = dict() #type -> Rule
        self.named_by_value = dict()
        self.named_rules = dict() #(param_name, type) -> Rule
        self.implementation = None
    
    # We implement the __get__ attribute descriptor protocol in order to make
    # MultiMethods appear as methods on new-style class instances.
    def __get__(self, instance, owner):
        if instance:
            return MethodType(self, instance, owner)
        else:
            return self
    
    def extend(self, *types):
        def register(func):
            if isinstance(func, MultiMethod):
                assert func is self #Multimethods shouldn't be "mixed" like this, should they?
                func = func.last_registered_function
            defaults = []
            if func.func_defaults:
                defaults = func.func_defaults
            self.addRule(types, func.func_code.co_varnames, defaults, func)
            self.last_registered_function = func
            return self
        return register
    
    def addRule(self, types, names, defaults, method):
        """
        Adds a new rule to the MultiMethod.
        
        Parameters:
            types: List containing the match criteria
            names: List of the parameters names. Necessary for supporing
                   keyword arguments
            defaults: Default values for the last len(defaults) parameters.
                      This list is used to provide default parameter matching.
            method: The function that gets called on a match.
        
        If a matching rule already exists, it is overwritten.
        """
        if not types:
            self.implementation = method
        else:
            if len(names) == len(defaults):
                new_defaults = defaults[1:]
            else:
                new_defaults = defaults
            if isinstance(types[0], ClassType) or isinstance(types[0], TypeType) or isinstance(types[0], ClassID):
                if types[0] not in self.rules:
                    self.rules[types[0]] = Rule()
                self.rules[types[0]].next.addRule(types[1:], names[1:], new_defaults, method)
                
                rule = Rule()
                if (names[0], types[0]) in self.named_rules:
                    rule = self.named_rules[(names[0], types[0])]
                rule.next.addRule(types[1:], names[1:], new_defaults, method)
                if len(defaults) == len(names):
                    rule.defaultable = True
                self.named_rules[(names[0], types[0])] = rule
            else:
                if types[0] not in self.by_value:
                    self.by_value[types[0]] = Rule()
                self.by_value[types[0]].next.addRule(types[1:], names[1:], new_defaults, method)
                
                rule = Rule()
                if (names[0], types[0]) in self.named_by_value:
                    rule = self.named_by_value[(names[0], types[0])]
                rule.next.addRule(types[1:], names[1:], new_defaults, method)
                self.named_by_value[(names[0], types[0])] = rule
    
    def __call__(self, *args, **named):
        return self.invoke(args, named)
    
    def invoke(self, args, named):
        """
        Invoke the MultiMethod
        
        Note:  The preferred way of invoking a MultiMethod is through __call__
        
        Parameters:
            args: list of values for positional arguments
            named: dictionary of name->value mappings for keyword arguments
        """
        method = self.resolve(args, named)
        #print "(%s, %s) -> %s)" % (str(args), str(named), str(method))
        if not method:
            raise NotImplementedError("Operation not supported with given parameters", args,named)
        return method(*args, **named)
    
    def resolve(self, args, kwargs):
        #print "resolve(%s, %s)" % (str(args), str(kwargs))
        if not args:
            if not kwargs:
                if self.implementation:
                    return self.implementation
                return self.resolveDefaults()
            else:
                return self.resolveKeywords(kwargs)
        
        function = self.resolveByValue(args[0], args[1:], kwargs)
        if function:
            return function
        return self.resolveByType(args[0].__class__, args[1:], kwargs)
    
    def resolveByValue(self, value, args, kwargs):
        try: #Necessary, for now at least, in case value is not hashable
            if value in self.by_value:
                return self.by_value[value].next.resolve(args, kwargs)
        except: pass
        return None
    
    def resolveByType(self, type, args, named):
        function = None
        if type in self.rules:
            function = self.rules[type].next.resolve(args, named)
        elif hasattr(type, "CLASS_ID") and type.CLASS_ID in self.rules:
            function = self.rules[type.CLASS_ID].next.resolve(args, named)
        if function:
            return function
        return self.resolveBaseClasses(type, args, named)
    
    def resolveBaseClasses(self, type, args, named):
        for t in _mro(type):
            if t in self.rules:
                function = self.rules[t].next.resolve(args, named)
                if function:
                    return function
            elif hasattr(t, "CLASS_ID") and t.CLASS_ID in self.rules:
                function = self.rules[t.CLASS_ID].next.resolve(args, named)
                if function:
                    return function
        return None
    
    def resolveDefaults(self):
        for key in self.named_rules:
            rule = self.named_rules[key]
            if rule.defaultable:
                if rule.next.implementation:
                    return rule.next.implementation
                else:
                    value = rule.next.resolveDefaults()
                    if value:
                        return value
        return None
    
    def resolveKeywords(self, named):
        defaultable = []
        for name in named:
            value = named[name]
            if not isinstance(value, list):
                #print "Trying (%s, %s)" % (str(name), str(value))
                if (name, value) in self.named_by_value:
                    #print "Potential match found!"
                    names = named.copy()
                    del names[name]
                    function = self.named_by_value[(name, value)].next.resolve([], names)
                    if function:
                        #print "Match Found!"
                        return function
        for key in self.named_rules:
            rule = self.named_rules[key]
            for name in named:
                value = named[name]
                #print "testing", (name, value), "against", key
                if name==key[0] and _isinstance(value, key[1]):
                    names = named.copy()
                    del names[name]
                    method = None
                    if not names and rule.next.implementation:
                        method = rule.next.implementation
                    elif rule.next:
                        method = rule.next.resolve([], names)
                    if method:
                        return method
                elif name!=key[0] and rule.defaultable and rule.next:
                    defaultable.append(rule)
            for rule in defaultable:
                method = rule.next.resolve([], named)
                if method:
                    return method

__registry__ = dict()
__last_registered__ = dict()

registerMultiMethod = MultiMethod()

def __registerFunction__(name, func, types):
    #print "%s -> %s" % (str(types), str(func))
    if __registry__.has_key(name):
        mm = __registry__[name]
    else:
        mm = MultiMethod()
        __registry__[name] = mm
    return mm.extend(*types)(func)

registerMultiMethod.addRule((str, FunctionType, list), ["name", "func", "types"], [], __registerFunction__)

def __registerMultiMethod__(name, func, types):
    func = __last_registered__[(name)]
    return registerMultiMethod(name, func, types)

registerMultiMethod.addRule((str, MultiMethod, list), ["name", "func", "types"], [], __registerMultiMethod__)

def multimethod(*types):
    def register(func):
        if isinstance(func, MultiMethod):
            func = func.last_registered_function
        return __registerFunction__(func.__name__, func, types)
    return register
