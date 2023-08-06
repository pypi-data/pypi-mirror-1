# -*- coding: utf-8 -*-
"""Recipe i18noverrides"""

import logging
import os
import shutil
import sys

logger = logging.getLogger('collective.recipe.i18noverrides')


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        """Installer"""
        #print self.options
        source = self.options.get('source')
        destinations = self.options.get('destinations')
        destinations = [d for d in destinations.splitlines() if d]
        for dir in [source] + destinations:
            if not os.path.exists(dir):
                logger.error('path %r does not exist.', dir)
                sys.exit(1)
            if not os.path.isdir(dir):
                logger.error('path %r must be a directory.', dir)
                sys.exit(1)

        po_files = [f for f in os.listdir(source) if f.endswith('.po')]
        if len(po_files) == 0:
            logger.warn('source %r contains no .po files.', source)
            return tuple()

        created = []
        for destination in destinations:
            i18n_dir = os.path.join(destination, 'i18n')
            if not os.path.exists(i18n_dir):
                logger.info("Creating directory %s" % i18n_dir)
                os.mkdir(i18n_dir)
                created.append(i18n_dir)
            if not os.path.isdir(i18n_dir):
                logger.error("%r is not a directory." % i18n_dir)
                sys.exit(1)
            for po_file in po_files:
                file_path = os.path.join(source, po_file)
                shutil.copy(file_path, i18n_dir)
                created.append(os.path.join(i18n_dir, po_file))

        logger.info('Copied %d po files.' % len(po_files))

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.

        # XXX Returning 'created' here gives test errors now.  We will
        # have to see if this is really needed in our use case, as the
        # zope instances likely get removed anyway.  But if a source
        # file was removed meanwhile, we will have to remove it in the
        # destinations as well.  But zc.buildout should do this
        # automatically and even when returning 'created' I do not see
        # that happening.  So we will ignore it.
        return tuple()

    # It is easiest if the updater does the same as the installer.
    update = install
