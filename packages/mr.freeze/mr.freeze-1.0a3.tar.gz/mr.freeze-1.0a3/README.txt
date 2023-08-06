Introduction
============

This package allows one to perform various debugging and development actions
on a running Zope instance.  In order to perform an action one must:

  1. Insert a command into a special control file.  To determine which file
     to look in, mr.freeze will take the Zope pid file and replace the
     extension with '.freeze'.  So in a typical buildout the control file
     would be var/instance.freeze
  2. Send a *USR1* signal to the Zope instance.

This pattern is intended to support integration with editors like TextMate
and emacs, but that hasn't been implemented yet.


Commands
========

The following commands are currently supported in both debug and non-debug mode.

stack
  Will dump a stack backtrace for all threads to the console.
  (Default command if unable to read freeze file.)

pony
  Will dump a pony to the console.


The following commands are supported in debug mode only.

freeze
  Will drop Zope to a pdb debug prompt.

freeze [file] [line #]
  Will set a pdb breakpoint on the specified line.


The following commands are planned.

reload code
  Will reload code that has been modified.

reload zcml
  Will reload code and ZCML that has been modified.


Editor integration
==================

Please see r82128_ for some preliminary information regarding TextMate_
integration or watch the quick `demo screen cast`__.

  .. _r82128: http://dev.plone.org/collective/changeset/82128
  .. _TextMate: http://macromates.com/
  .. __: http://www.vimeo.com/3595417

Credits
=======

 * David Glick
 * Andreas Zeidler

Thanks to those who have helped provide the foundation for this package:

 * Products.signalstack: Wichert Akkerman
 * Products.PDBDebugMode: Ross Patterson
 * z3c.deadlockdebugger: Malthe Borch
 * DeadlockDebugger: Florent Guillaume
 * threadframe: Fazal Majid
