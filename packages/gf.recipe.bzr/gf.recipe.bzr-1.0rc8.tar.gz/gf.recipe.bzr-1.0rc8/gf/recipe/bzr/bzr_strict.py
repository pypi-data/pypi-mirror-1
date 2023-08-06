import re
import os
import sys
import logging
import subprocess
import zc.buildout
from gf.recipe.bzr import bzr
from gf.recipe.bzr.bzr import re_pull_location, execute, add_password, BZR

re_extra_rev = re.compile(r'(^|\n)You have \d+ extra revision\(s\):')
re_push_location = re.compile(r'push branch: ([^\n]*)\n')

class BzrRecipe(bzr.BzrRecipe):

    strict = True

def setup_logging(logger):
    # Set the same level as the zc
    zc_logger = logging.getLogger('zc.buildout')
    level = zc_logger.level
    logger.setLevel(level)

def uninstallBzrRecipe(name, options):
    # Set the same level as the zc
    logger = logging.getLogger(name)
    setup_logging(logger)
    # Iterate on all subdirs.
    root_dir = options['root_dir']
    # If the root dir does not exist, we have nothing to check.
    if not os.path.isdir(root_dir):
        return
    for dirname in os.listdir(root_dir):
        if dirname.startswith("."):
            # A VCS directory, or a hidden directory, skip
            continue
        path = os.path.join(root_dir, dirname)
        if not os.path.exists(os.path.join(path, ".bzr")):
            # Not a bzr branch or checkout
            continue
        os.chdir(path)
        # See if there are uncommitted changes
        cmd = BZR + ' st'
        stdout, stderr = execute(cmd, logger)
        if stdout or stderr:
            logger.error(
                'Abort uninstalling "%s" (commit or adjust .bzrignore?), detailed output follows:\n"""\n%s\n%s"""',
                dirname, stdout, stderr)
            break
        # We need to acquire the push location, since bzr missing otherwise would
        # act on the pull location.
        cmd = BZR + ' info'
        stdout, stderr = execute(cmd, logger)
        match = re_push_location.search(stdout)
        if stderr:
            logger.error(
                'Abort uninstalling "%s" (not a bzr branch, or no push and pull location?), detailed output follows:\n"""\n%s\n%s"""',
                dirname, stdout, stderr)
            break
        if match is not None:
            location = match.group(1)
        else:
            match = re_pull_location.search(stdout)
            if match is None:
                logger.error(
                    'Abort uninstalling "%s" (not a bzr branch, or no push and pull location?), detailed output follows:\n"""\n%s\n%s"""',
                    dirname, stdout, stderr)
                break
            location = match.group(1)
            logger.debug(
                'Push location not found, using pull location for "%s", detailed output follows:\n"""\n%s\n%s"""',
                dirname, stdout, stderr)
        # Add password (if any) to location
        location = add_password(options, location)
        # See if something is not pushed to upstream
        cmd = '%s missing %s' % (BZR, location)
        stdout, stderr = execute(cmd, logger)
        if stderr or re_extra_rev.search(stdout):
            logger.error(
                'Abort uninstalling "%s" (push or adjust push location?), detailed output follows:\n"""\n%s\n%s"""',
                dirname, stdout, stderr)
            break
    else:
        # Ok.
        return
    raise zc.buildout.UserError('Abort uninstalling, because of pending local changes.')
