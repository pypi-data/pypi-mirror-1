# -*- coding: utf-8 -*-
"""Logcheck recipe"""
import logging
import os

logger = logging.getLogger('logcheck')

NEEDED_SUBDIRS= ('cracking.d',
                 'cracking.ignore.d',
                 'violations.d',
                 'violations.ignore.d',
                 'ignore.d.paranoid',
                 'ignore.d.server',
                 'ignore.d.workstation')

CONF_TEMPLATE = '''
REPORTLEVEL="workstation"
SENDMAILTO="%(recipient)s"
FQDN=0
RULEDIR="%(part_dir)s"
LOCKFILE="%(var_dir)s/lock"
LOGFILES_LIST="%(part_dir)s/logcheck.logfiles"
STATEDIR="%(var_dir)s/state"
EVENTSSUBJECT="%(subject)s"
'''


class Recipe(object):
    """Recipe for installing logcheck configuration files"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.buildout_dir = self.buildout['buildout']['directory']
        var_dir = os.path.abspath(
            os.path.join(self.buildout_dir, 'var', self.name))
        part_dir = os.path.abspath(
            os.path.join(self.buildout_dir, 'parts', self.name))
        state_dir = os.path.abspath(
            os.path.join(var_dir, 'state'))
        self.options['var_dir'] = var_dir
        self.options['part_dir'] = part_dir
        self.options['state_dir'] = state_dir
        self.recipient = self.options['recipient']

        self.logfiles = [f for f in self.options['logfiles'].split() if f]
        self.logfiles = [os.path.join(self.buildout_dir, f) for f in
                         self.logfiles]

        options.setdefault('subject', self.logfiles[0])
        options.setdefault('ignores', '')
        self.ignores = [i for i in self.options['ignores'].split('\n') if i]
        # File locations.
        self.generic_config = os.path.join(part_dir, 'logcheck.conf')
        self.logfiles_config = os.path.join(part_dir, 'logcheck.logfiles')
        self.ignore_file = os.path.join(part_dir,
                                        'ignore.d.workstation',
                                        '%s-ignores' % self.name)
        # Crontab command
        self.options['command'] = '/usr/sbin/logcheck -c %s' % (
            self.generic_config)

    def install(self):
        """Make sure all directories/files exist and install configuration."""
        # Make sure directories exist.
        for directory in (self.options['var_dir'],
                          self.options['state_dir'],
                          self.options['part_dir']):
            if not os.path.isdir(directory):
                os.makedirs(directory)
                logger.info('Created %s', directory)
        for needed in NEEDED_SUBDIRS:
            directory = os.path.join(self.options['part_dir'], needed)
            if not os.path.isdir(directory):
                os.makedirs(directory)
                logger.info('Created %s', directory)
        # Create config files.
        contents = CONF_TEMPLATE % dict(
            recipient=self.recipient,
            part_dir=self.options['part_dir'],
            var_dir=self.options['var_dir'],
            subject=self.options['subject'])
        open(self.generic_config, 'w').write(contents)
        contents = '\n'.join(self.logfiles)
        open(self.logfiles_config, 'w').write(contents)
        # Handle regex's
        if self.ignores:
            contents ='\n'.join(self.ignores) + '\n'
            open(self.ignore_file, 'w').write(contents)
            logger.info("Writing file with %s ignore patterns: %s",
                        len(self.ignores), self.ignore_file)
        else:
            if os.path.exists(self.ignore_file):
                os.remove(self.ignore_file)
        return tuple()

    def update(self):
        """When there are no changes, there's nothing to do."""
        pass
