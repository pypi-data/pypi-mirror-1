Detailed documentation
======================

Supported options
-----------------

The recipe supports the following options:

logfiles
    Logfiles is a list of one or more logfiles that should be handled by the
    logcheck utility.  This parameter is required.

recipient
    One (?TODO: check) email address to serve as recipient of the logcheck
    emails.  This parameter is required.

ignores
    Several optional lines of regex expressions. If a regex matches, the
    matching line is excluded from the logcheck email.

subject
    Subject used in the email subject.  (Note: only part of the subject,
    logcheck itself appends/prepends the date and so.)  Defaults to logfile
    path instead of the unhelpful "System Events" default of logcheck itself.


Example usage
-------------

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = logcheck
    ...
    ... [logcheck]
    ... recipe = tha.recipe.logcheck
    ... logfiles = var/example.log
    ... recipient = someone@example.com
    ... subject = my site
    ... """)

Running the buildout installs a directory structure in parts and var::

    >>> print 'start', system(buildout) 
    start...
    Installing logcheck.
    logcheck: Created /sample-buildout/var/logcheck
    logcheck: Created /sample-buildout/var/logcheck/state
    logcheck: Created /sample-buildout/parts/logcheck
    logcheck: Created /sample-buildout/parts/logcheck/cracking.d
    logcheck: Created /sample-buildout/parts/logcheck/cracking.ignore.d
    logcheck: Created /sample-buildout/parts/logcheck/violations.d
    logcheck: Created /sample-buildout/parts/logcheck/violations.ignore.d
    logcheck: Created /sample-buildout/parts/logcheck/ignore.d.paranoid
    logcheck: Created /sample-buildout/parts/logcheck/ignore.d.server
    logcheck: Created /sample-buildout/parts/logcheck/ignore.d.workstation
    <BLANKLINE>
    >>> ls('var/logcheck')
    d  state
    >>> ls('parts/logcheck')
    d  cracking.d
    d  cracking.ignore.d
    d  ignore.d.paranoid
    d  ignore.d.server
    d  ignore.d.workstation
    -  logcheck.conf
    -  logcheck.logfiles
    d  violations.d
    d  violations.ignore.d
    >>> ls('bin')
    -  buildout

The logfiles config file lists the logfiles::

    >>> cat('parts/logcheck/logcheck.logfiles')
    /sample-buildout/var/example.log

The generic config file lists the right directories::

    >>> cat('parts/logcheck/logcheck.conf')
    REPORTLEVEL="workstation"
    SENDMAILTO="someone@example.com"
    FQDN=0
    RULEDIR="/sample-buildout/parts/logcheck"
    LOCKFILE="/sample-buildout/var/logcheck/lock"
    LOGFILES_LIST="/sample-buildout/parts/logcheck/logcheck.logfiles"
    STATEDIR="/sample-buildout/var/logcheck/state"
    EVENTSSUBJECT="my site"

If you don't specify a subject, the default fallback is the filename that is
checked (added in 0.4):

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = logcheck
    ...
    ... [logcheck]
    ... recipe = tha.recipe.logcheck
    ... logfiles = var/example.log
    ... recipient = someone@example.com
    ... """)
    >>> print 'start', system(buildout) 
    start Uninstalling logcheck.
    Installing logcheck.
    <BLANKLINE>
    >>> cat('parts/logcheck/logcheck.conf')
    REPORTLEVEL="workstation"
    SENDMAILTO="someone@example.com"
    FQDN=0
    RULEDIR="/sample-buildout/parts/logcheck"
    LOCKFILE="/sample-buildout/var/logcheck/lock"
    LOGFILES_LIST="/sample-buildout/parts/logcheck/logcheck.logfiles"
    STATEDIR="/sample-buildout/var/logcheck/state"
    EVENTSSUBJECT="/sample-buildout/var/example.log"


Specifiying two logfiles is possible

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = logcheck
    ...
    ... [logcheck]
    ... recipe = tha.recipe.logcheck
    ... logfiles =
    ...     var/example.log
    ...     var/emergency.log
    ... recipient = someone@example.com
    ... subject = my site
    ... """)
    >>> print 'start', system(buildout) 
    start Uninstalling logcheck.
    Installing logcheck.
    <BLANKLINE>
    >>> cat('parts/logcheck/logcheck.logfiles')
    /sample-buildout/var/example.log
    /sample-buildout/var/emergency.log    


Strategy
--------

The logcheck setup done by this recipe is very simple.  The needed logcheck
directories are created, but mostly left empty.  This means that all logfile
messages are, in principle, mailed.

This is obviously not intended.  Therefore the ``ignore.d.workstation``
directory has one file with ignore regex's if you specified them.

    >>> ls('parts/logcheck/ignore.d.workstation')

We specify a regex::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = logcheck
    ...
    ... [logcheck]
    ... recipe = tha.recipe.logcheck
    ... logfiles = var/example.log
    ... recipient = someone@example.com
    ... ignores =
    ...     ^.+INFO.*
    ... """)

    >>> print 'start', system(buildout) 
    start...
    Uninstalling logcheck.
    Installing logcheck.
    logcheck: Writing file with 1 ignore patterns: /...station/logcheck-ignores
    <BLANKLINE>

    >>> ls('parts/logcheck/ignore.d.workstation')
    -   logcheck-ignores
    >>> cat ('parts/logcheck/ignore.d.workstation/logcheck-ignores')
    ^.+INFO.*

Logcheck is supposed to be called from a cronjob. The recipe provides an
option that lists the correct command that can be used from other
recipes::

    >>> write('crontab', '')
    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = logcheck crontab
    ...
    ... [logcheck]
    ... recipe = tha.recipe.logcheck
    ... logfiles = var/example.log
    ... recipient = someone@example.com
    ... ignores =
    ...     ^.+INFO.*
    ... 
    ... [crontab]
    ... recipe = z3c.recipe.usercrontab
    ... times = */5 * * * *
    ... command = ${logcheck:command}
    ... readcrontab = cat ${buildout:directory}/crontab
    ... writecrontab = cat > ${buildout:directory}/crontab
    ... 
    ... """)
    >>> print 'start', system(buildout) 
    start...
    Updating logcheck.
    Installing crontab.
    >>> cat('crontab')
    <BLANKLINE>
    # Generated by /sample-buildout [crontab]
    */5 * * * * /usr/sbin/logcheck -c /sample-buildout/parts/logcheck/logcheck.conf
    # END /sample-buildout [crontab]
    <BLANKLINE>

