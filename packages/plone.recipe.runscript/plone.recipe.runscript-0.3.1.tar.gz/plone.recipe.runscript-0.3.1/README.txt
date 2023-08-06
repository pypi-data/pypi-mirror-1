Plone Runscript Recipe
======================

Abstract
--------

This is a buildout recipe for zope/plone which runs a script
using **zopectl** in a zope instance.

Recipe options
--------------

instance-home
  The INSTANCE_HOME. This can commonly be found in the ${instance:location}
  buildout variables.

zeo-home
  If you are using a zeo server then you must define this option so zopectl
  can connect to your database.  This can commonly be found in the
  ${zeoserver:location} buildout variable.

script
  The path to the script that will be run. If not specified the script name
  is taken form the part name with a ``.py`` suffix added  and assumed to be
  location in ${buildout:bin-directory}.

args
  The arguments for the script.

The script is run using the instance startup script, which is assumed to be
named like the basename part of the instance-home directory.

