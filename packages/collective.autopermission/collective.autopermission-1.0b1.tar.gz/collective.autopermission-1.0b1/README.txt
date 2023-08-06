Introduction
============

This package registers an event handler that initialises permissions on the
fly. To use it, simply include its ZCML:

    <include package="collective.autopermission" />
    
Then, you can use the <permission /> ZCML statement to define a new type of
permission, without also needing to make the permission "spring into
existence" via ClassSecurityInfo or similar.
