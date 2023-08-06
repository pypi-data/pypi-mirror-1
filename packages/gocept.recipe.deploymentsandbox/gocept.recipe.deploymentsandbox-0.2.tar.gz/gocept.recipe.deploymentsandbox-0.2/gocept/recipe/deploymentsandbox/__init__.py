# -*- coding: utf-8 -*-
"""Recipe deploymentsandbox"""

import os
import os.path


SANDBOX_DIRS = {
    'etc-directory': 'etc/%(name)s',
    'log-directory': 'var/log/%(name)s',
    'run-directory': 'var/run/%(name)s',
    'crontab-directory': 'etc/cron.d',
    'logrotate-directory': 'etc/logrotate.d',
    'rc-directory': 'etc/init.d',
}

# Make directory paths platform independent
SANDBOX_DIRS = dict((name, path.split('/'))
                    for (name, path) in SANDBOX_DIRS.items())


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        if options.get('name', None) is None:
            options['name'] = name

        options['user'] = os.environ['LOGNAME']

        self.root = self.options.get(
            'root',
            os.path.join(self.buildout['buildout']['parts-directory'],
                         self.name))

        # Compute zc.recipe.deployment-compatible options.
        # This needs to happen early so that other recipes can pick those paths up.
        for option, path in SANDBOX_DIRS.items():
            if option not in options:
                options[option] = os.path.join(self.root, *path) % options

    def install(self):
        """Installer"""
        # Create sandbox directories
        for option in SANDBOX_DIRS:
            target = self.options[option]
            if not os.path.isdir(target):
                os.makedirs(target)

        # We do not notify buildout about the created directories to avoid
        # deleting data.
        return tuple()

    def update(self):
        """Updater"""
        # Just make sure that all directories are still there.
        self.install()
