Plone Runscript Recipe
======================

:Author:  Stefan Eletzhofer <stefan.eletzhofer@inquant.de>
:Date:    $Date: 2007-06-03 22:24:17 +0200 (Sun, 03 Jun 2007) $
:Revision: $Revision: 43085 $

Abstract
--------

This is a buildout recipe for zope/plone which runs a script
using **zopectl** in a zope instance.

Recipe options
--------------

instance-home
  The INSTANCE_HOME

args
  The arguments for the script

The name of the script is created from the section name and is assumed to
be in the ${buildout:bin-directory}.

The script is the run using the instance startup script, which is assumed
to be named like the basename part of the instance-home directory.
