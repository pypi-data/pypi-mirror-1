# -*- coding: ascii -*-
# $Id$
# $Source$
# $Author$
# $HeadURL$
# $Revision$
# $Date$
'''
    pyrole.role:

        Module for creating roles.

    author: Ask Solem <askh@opera.com>
    Copyright (c) Ask Solem. Released under the Modified BSD-license, see the
    LICENSE file for a full copy of the license.
'''

__version__     = '0.11'
__author__      = 'Ask Solem <askh@opera.com'
__authority__   = 'pypi:ASK'

from roleplay.meta import MetaRole

class ClassDoesNotFulfillRequirement(Exception):
    ''' Tried to apply role to the class, but the class didn't fulfill
        all requirements of the role. (Probably missing method/attribute)
    '''

class Role(object):
    ''' -------------------------------------------  --- ---- -   - -  - -
        Base class for Roles.

        New roles inherits from this.
    ---------------------------------------------------------------------- '''
    meta = MetaRole()

    def __init__(self, instance, **kwargs):
        self.meta.init_attributes(self, for_class=instance, role_args=kwargs)

    def apply_attribute(self, attr_name, attr_value):
        for_class = self.for_class
        self.meta.apply_attribute(for_class, attr_name, attr_value)

    def __buildrole__(self):
        ''' 
            Builds the role using the MetaRole class.
            If the role defines the '__requires__' attribute it
            also checks if the user class adheres to the
            required interface. (See 'check_requires' for more info)

        '''
       
        # Since we only do it by instance now we have to add
        # the role for every constructed instance :( 
        '''    
        # Just return if the class already does this role.
        for_class = self.for_class
        if self.meta.__does__(for_class, self):
            return
        '''

        if hasattr(self, '__requires__'):
            self.check_requires()

        self.meta.__buildrole__(self)

    def check_requires(self):
        '''
            The role can have a 'requires' attribute containing a list of
            attribute-names that the user class has to implement to do the
            role. This method will check that all requirements are fulfilled.
        '''
        for_class = self.for_class

        for requirement in self.__requires__:
            if not hasattr(for_class, requirement):
                raise ClassDoesNotFulfillRequirement(requirement)


# Local Variables:
#   mode: cpython
#   cpython-indent-level: 4
#   fill-column: 78
# End:
# vim: expandtab tabstop=4 shiftwidth=4 shiftround
