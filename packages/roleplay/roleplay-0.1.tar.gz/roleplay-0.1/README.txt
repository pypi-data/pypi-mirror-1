 
roleplay: Python does Roles

        Implements Roles for Python.

        See the Traits paper[1], Perl 6 Synopsis + Apocalypse 12[2]
        for more information.


        This is an alpha release, any suggestions, patches and bug reports
        welcome.

        Traits: Composable Units of Behaviour
        Nathanael Sch¨arli, St´ephane Ducasse, Oscar Nierstrasz, and Andrew P. Black 
        [1] http://www.iam.unibe.ch/~scg/Archive/Papers/Scha03aTraits.pdf

        [2] Perl 6 Synopsis 12: Objects: Roles
            http://dev.perl.org/perl6/doc/design/syn/S12.html#roles  

            Perl 6 Apocalypse 12: Objects
            http://dev.perl.org/perl6/doc/design/apo/A12.html 
         

        

        SYNOPSIS

        >>> from roleplay.role import Role
        
        >>> class RevisionRole(Role):
        ...     '''
        ...         First we create a role. This is a stub for a role
        ...         that implements version control on database tables
        ...     '''
        ...
        ...     # All Roles has by default the "for_class" and 'role_args'
        ...     # attributes. "for_class" can either be object instance or
        ...     # class object.
        ...
        ...     def add_revision(self, data):
        ...         for_class = self.for_class
        ...         role_args = self.role_args
        ...
        ...         table           = role_args['table']
        ...         primary_key_col = role_args['primary_key_col']
        ...     
        ...         # Do something with data
        ...         # .....
        ...
        ...
        ...     # Roles can use the '__requires__' attribute to define a set
        ...     # of attributes/methods the class using the role has to
        ...     # define (or else it would get an exception).
        ...     
        ...     __requires__ = "username password".split()
        
      
        >>> from roleplay import has_role, does
 
        >>> class Article(object): 
        ...     '''
        ...         This is our class using the revisions role.
        ...         Imagine it's a class representing a newspaper article,
        ...         that will support revisions if it does the revisions role
        ...         (This could even be defined in a configuration file).
        ...     '''
        ...
        ...     def __init__(self):
        ...         has_role(self, RevisionRole)
        ...
        ... 
        ...     def save_article(self, data):
        ...         
        ...         if does(self, 'RevisionRole'):
        ...             self.add_revision(data)
        ...
        ...         # ... save the article .. #
        ...
        ...


    To install:

        python ./setup.py install


    Or via easy_install:

        easy_install roleplay

        


    author: Ask Solem <askh@opera.com>
    Copyright (c) Ask Solem. Released under the Modified BSD-license, see the
    LICENSE file for a full copy of the license.
