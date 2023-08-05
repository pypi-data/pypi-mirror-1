# -*- coding: ascii -*-
# $Id$
# $Source$
# $Author$
# $HeadURL$
# $Revision$
# $Date$
'''
    roleplay.meta:

        This module handles internal role metadata and the introspection
        necessary to install roles and mixin classes.

    author: Ask Solem <askh@opera.com>
    Copyright (c) Ask Solem. Released under the Modified BSD-license, see the
    LICENSE file for a full copy of the license.
'''

__version__     = '0.1'
__author__      = 'Ask Solem <askh@opera.com'
__authority__   = 'pypi:ASK'

import os
import sys
import types
import inspect
from   itertools import ifilter
from   inspect   import isbuiltin

DEBUG = 0

roles_defines_attrs = "check_requires for_class role_args meta".split()

# ##### EXCEPTIONS

class AttributeIsPrototypeError(Exception):
    ''' The attribute is only a prototype and is not accessible '''

# #### DEBUGGING
def _announce_symbol_exported(from_class, symbol, into):
    ''' MetaRole._mixin() uses this to print whenever a symbol was exported
        in DEBUG mode
    '''
    print (">>> Role %(from_class)s: "
           "Exporting symbol [%(symbol)s] into %(into)s" % locals())

def get_class_name(cls):
    '''
        Given a class, instance or string this always
        tries to return the class name
    '''
    name = ""
    if isinstance(cls, object):
        if hasattr(cls, '__name__'):
            name = cls.__name__
        else:   # is instance
            name = cls.__class__.__name__
    else:
        name = cls
    return name

class MetaRoleRegistry(object):
    '''
        Keeps track of classes and their roles.
    '''
    _shared_state   = { }
    _role_registry  = { }
    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._shared_state
        return obj

    def get_roles_for_class(self, cls):
        name = get_class_name(cls)
        if name not in self._role_registry:
            self._role_registry[name] = { }
        return self._role_registry[name]
            
class MetaRole(object):
    ''' -------------------------------------------  --- ---- -   - -  - -
        Roles metadata.

        Probably only used by the Role class itself. If you want to
        subclass the role system, it's probably better to subclass Role
        rather than MetaRole.
    ---------------------------------------------------------------------- '''

    # ### Prototype attributes
    # only here so they can be skipped when mixing.
    for_class  = None
    role_args  = None
    meta       = None

    # ### Registry composite
    role_registry = MetaRoleRegistry()
        
    
    def __buildrole__(self, role_class):
        ''' This is the step that installs the role into the class. '''
        self._mixin(role_class, role_class.for_class)
        self.__addrole__(role_class.for_class, role_class)

    def __does__(self, cls, role):
        ''' private method doing the role lookup '''
        roles_for = self.role_registry.get_roles_for_class(cls)
        role_name = get_class_name(role)
        if role_name in roles_for:
            return True
        else:
            return False

    def __addrole__(self, cls, role):
        ''' private method updating the role registry '''
        roles_for = self.role_registry.get_roles_for_class(cls)
        role_name = get_class_name(role)
        roles_for[role_name] = True

    def init_attributes(self, cls, **kwargs):
        '''
            Initialize multiple attributes at once, with default values.
            Usually used within the __init__ method of a class.

            Example usage:

                class MyRole(Role):
                    meta = MetaRole()

                    def __init__(self, for_class):
                        meta.init_attributes(self,
                            for_class=for_class,
                        )

            This will initialize the attributes for_class
            with the default values passed when constructing the instance.
        '''
        [setattr(cls, name, value) for name, value in kwargs.iteritems()]

    def apply_attribute(self, for_class, attribute_name, attribute_value):
        if hasattr(for_class, attribute_name):
            return
        setattr(for_class, attribute_name, attribute_value)


    def __getattribute__(self, attribute_name):
        ''' Same as the usual __getattr__ except it will raise an
            AttributeIsPrototypeError when accessing any attributes
            that just defines the instance of a real Role.
        '''
        if attribute_name in roles_defines_attrs:
            raise AttributeIsPrototypeError
        return super(MetaRole, self).__getattribute__(attribute_name)

    def _get_normalized_symtable(self, from_object):
        '''
            Get a list of normalized symbols from an object.

            This is like dir(from_object), except it will not contain
            symbols from builtin methods, the type metaclass,
            or the MetaRole class.
        '''
        results = []
        for symbol in dir(from_object):
            if symbol in skip_sym:
                continue
            value = getattr(from_object, symbol)
            if isinstance(value, types.MethodType):
                results.append((symbol, value))
        return results

    def _mixin(self, from_class, into_other):
        '''
            Installs all attributes/methods in the role into the do'ing
            class that the class has not defined.

            It will not install builtin methods or attributes/methods from
            object (the type metaclass), or the MetaRole class.
        '''
        others_symtable = set( dir(into_other) )
        
        for symbol, symbol_ref in self._get_normalized_symtable(from_class):

            if (not isbuiltin(symbol_ref) and symbol not in others_symtable):
                setattr(into_other, symbol, symbol_ref)

                if DEBUG: _announce_symbol_exported(from_class, symbol, into_other)


'''
set: skip_sym
    Used by MetaRole._get_normalized_symtable_for() as a list of
    attributes/methods we don't export when doing a mixin.
'''  
skip_sym = set( dir(MetaRole) )
skip_sym.add('__metaclass__')

# Local Variables:
#   mode: cpython
#   cpython-indent-level: 4
#   fill-column: 78
# End:
# vim: expandtab tabstop=4 shiftwidth=4 shiftround
