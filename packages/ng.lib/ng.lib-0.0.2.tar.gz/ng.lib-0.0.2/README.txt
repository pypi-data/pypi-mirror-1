Short module description
=========================

Module pd.lib content some simple modules
and fucntions for use in Zope.

Description of modules
----------------------

ng.lib.interface
................

The module to provide different small tools to deal with interfaces in Zope.

Function provided by module followed:

    implements
        Function implements must be issued with interfaces as arguments.
        As original zope.interface.implements, our function make context
        class provided  this interfaces. In difference from original function,
        our implementation added for each field of each interface name attribute
        of FieldProperty type.
