Simple logcheck recipe
======================

Applications that generate logfiles inside your buildout can profit from
regular, you know, actually *checking* those logfiles.

`Logcheck <http://logcheck.org>`_ is a unix utility that can go through your
logfiles and that will mail you those lines that you find interesting,
provided you configure it right with ignores.

tha.recipe.logcheck provides a simple way of setting up a set of local
configuration files for logcheck.  To actually use it, z3c.recipe.usercrontab
is recommended. A ``${logcheck:command}`` option is available for easy
integration.
