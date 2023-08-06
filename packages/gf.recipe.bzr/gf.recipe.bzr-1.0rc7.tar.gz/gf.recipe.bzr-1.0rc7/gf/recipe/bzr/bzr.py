
import re
import os
import sys
import urlparse
import shutil
import subprocess
import logging
import zc.buildout

# No need to specify '.bat' or '.exe' extension on Windows, PATHEXT
# will take care of it.
BZR = 'bzr'
is_win32 = sys.platform == "win32"


def execute(cmd, logger):
    logger.debug('Calling bazaar in %s:\n  %s',
        os.getcwd(), cmd)
    # Feed it a bunch of newlines, in case it asks for password
    # (if you use password authentication, install pycurl
    # and specify the newlines in .netrc
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            close_fds=not is_win32)
    stdout, stderr = proc.communicate(input="\n\n\n")
    return stdout, stderr

def setup_logging(logger):
    # Set the same level as the zc
    zc_logger = logging.getLogger('zc.buildout')
    level = zc_logger.level
    logger.setLevel(level)

# specifically, we want to avoid matching bzr+ssh://
# in the following url scheme
re_add_passwd = re.compile(r'^(.*https?://)([^@]*@)?(.*)$')

def add_password(options, location):
    http_authentication = options.get('http_authentication', None)
    if http_authentication:
        match = re_add_passwd.match(location)
        if match is not None:
            location = '%s%s@%s' % (match.group(1), http_authentication, match.group(3))
    return location

re_pull_location = re.compile(r'parent branch: ([^\n]*)\n')

class BzrRecipe(object):
    """bzr recipe

    Example::

        [bzr]
        recipe = gf.recipe.bzr
        urls =
            http://bazaar.launchpad.net/~kissbooth/kss.plugin.sdnd/trunk kss.plugin.sdnd
            http://bazaar.launchpad.net/~kissbooth/kss.plugin.livesearch/trunk kss.plugin.livesearch
        in_parts = False
        http_authentication = username:password
        develop = True
        destination = /src/code

    For more information, consult the file docs/README.txt in the egg.
    """

    strict = False

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.setup_logging()

        in_parts = options.get('in_parts', 'false')
        if in_parts.lower() not in ('true', 'false'):
            self.logger.error(
                'Bad in_parts parameter "%s", allowed values: true or false',
                in_parts)
            raise zc.buildout.UserError('Bad in_parts parameter')

        options['develop'] = develop = options.get('develop', 'true')
        if develop.lower() not in ('true', 'false'):
            self.logger.error(
                'Bad develop parameter "%s", allowed values: true or false',
                develop)
            raise zc.buildout.UserError('Bad develop parameter')

        options['shared-repo'] = shared_repo = options.get('shared-repo', 'false')
        if shared_repo.lower() not in ('true', 'false'):
            self.logger.error(
                'Bad shared_repo parameter "%s", allowed values: true or false',
                shared_repo)
            raise zc.buildout.UserError('Bad shared_repo parameter')

        options['format'] = format = options.get('format', '')

        root_dir = buildout['buildout']['directory']
        if in_parts.lower() == 'true':
            root_dir =  os.path.join(root_dir, 'parts')

        options["destination"] = destination = options.get("destination", "")
        if destination:
            if in_parts.lower() == 'true':
                self.logger.error(
                    "Can't specify both in_parts and destination")
                raise zc.buildout.UserError("Destination and in_parts specified.")
            options["root_dir"] = root_dir = destination
        else:
            options['root_dir'] = root_dir = os.path.join(root_dir, name)

        # Process the branches.
        branches = []
        for line in options['urls'].splitlines():
            if line and not line.isspace():
                words = line.split()
                try:
                    repo, egg = words
                except ValueError:
                    self.logger.error(
                       'Bad line in urls, "%s". Each line must contain the bzr branch url followed by a space and the egg name.',
                       line)
                    raise zc.buildout.UserError('Bad bzr branch url specification')

                # Add password (if any) to location
                repo = add_password(self.options, repo)

                # See if there's a revisionspec specified as part of the URL
                revspec = None
                (scheme, netloc, path, query, fragment) = urlparse.urlsplit(repo)
                parts = path.rsplit("@", 1)
                if len(parts) > 1:
                    path, revspec = parts
                    repo = urlparse.urlunsplit(
                        (scheme, netloc, path, query, fragment))

                branches.append(dict(
                    egg = egg,
                    repo = repo,
                    revspec = revspec,
                    path = os.path.join(root_dir, egg),
                    ))
        self.branches = branches
        options['develop-eggs-directory'] = buildout['buildout']['develop-eggs-directory']

    def setup_logging(self):
        # Set the same level as the zc
        self.logger = logging.getLogger(self.name)
        setup_logging(self.logger)

    def execute(self, cmd):
        stdout, stderr = execute(cmd, self.logger)
        return stdout, stderr

    def install(self):
        root_dir = self.options['root_dir']
        if not os.path.isdir(root_dir):
            if self.options.get('shared-repo', 'false').lower() == 'true':
                cmd = BZR + ' init-repo'
                if self.options.get('format'):
                    cmd = cmd + ' --format=%s' % self.options['format']
                cmd = cmd + ' %s' % root_dir
                stdout, stderr = self.execute(cmd)
            else:
                os.mkdir(root_dir)

        offline = self.buildout['buildout'].get('offline', '').lower() == 'true'
        newest = self.buildout['buildout'].get('newest', '').lower() == 'true'

        # Process required branches
        for branch in self.branches:
            if not os.path.isdir(branch['path']):
                # this is not possible in offline mode
                if offline:
                    self.logger.error('Cannot get %s from bzr repository %s,' +
                        ' in offline mode.', branch['egg'], branch['repo'])
                    raise zc.buildout.UserError('Cannot use bzr in offline mode')
                self.logger.info('Getting %s from bzr repository %s',
                    branch['egg'], branch['repo'])
                self.bzr_get(branch)
            else:
                # Only update in online mode and if newest is
                # specified.
                if not offline and newest:
                    self.bzr_update(branch)
            # setup.py develop the egg.
            self.egg_develop(branch)

        # Never uninstall anything.
        return []

    def update(self):
        # No updates when offline
        if self.buildout['buildout'].get('offline', '').lower() == 'true':
            return
        self.install()

    def bzr_get(self, branch):
        # Checking out in a working tree may give exception
        # To be sure, we change to the root directory.
        os.chdir(self.options['root_dir'])

        # Getting by calling bazaar
        cmd = BZR + ' get --no-tree %(repo)s %(path)s' % branch
        if branch.get('revspec') is not None:
            cmd += ' -r%(revspec)s' % branch
        stdout, stderr = self.execute(cmd)

        # check for errors
        # stderr may be multi line, we check last line
        stderr_lines = stderr.splitlines()
        if not stderr_lines or not stderr_lines[-1].startswith('Branched'):
            self.logger.error(
                'Error calling bazaar in "%s", detailed output follows:\n"""\n%% %s\n\n%s\n%s"""',
                branch['egg'], cmd, stdout, stderr)
            raise zc.buildout.UserError('Error calling bzr')

        # Now, let's go to the working dir for checking out a working tree
        os.chdir(branch['path'])
        cmd = BZR + ' checkout'
        if branch.get('revspec') is not None:
            cmd += ' -r%(revspec)s' % branch
        stdout, stderr = self.execute(cmd)

    def bzr_update(self, branch):
        # Updating by calling bazaar
        os.chdir(branch['path'])

        # We need to acquire the pull location,
        # mainly because we may want to add the password to it.
        cmd = BZR + ' info'
        stdout, stderr = self.execute(cmd)
        match = re_pull_location.search(stdout)
        if stderr or match is None:
            # We won't stop buildout, but we give
            # an error about the case, to notify the user.
            if self.strict:
                self.logger.error(
                    'Abort uninstalling "%s" (not a bzr branch, or no pull location?), detailed output follows:\n"""\n%s\n%s"""',
                    branch['egg'], stdout, stderr)
                raise zc.buildout.UserError('Error calling bzr')
            else:
                self.logger.error(
                    'Update failed in "%s" (not a bzr branch, or no pull location?), detailed output follows:\n"""\n%% %s\n\n%s\n%s"""',
                    branch['egg'], cmd, stdout, stderr)
                return
        location = match.group(1)

        # Add password (if any) to location
        location = add_password(self.options, location)

        # Do the pull now
        cmd = '%s pull %s' % (BZR, location)
        if branch.get('revspec') is not None:
            cmd += ' -r%(revspec)s' % branch
        status = self.bzr_pull(cmd, branch)
        return status

    def bzr_pull(self, cmd, branch):

        os.chdir(branch['path'])

        stdout, stderr = self.execute(cmd)

        # check for errors

        if self.strict:
            # This is accepted. Needed if we created a local branch.
            if "No pull location known or specified" in stderr:
                self.logger.debug(
                    'Ignore problem in "%s" and continue, detailed output follows:\n"""\n%s\n%s"""',
                    branch['egg'], stdout, stderr)
                return True

        # This is ok.
        if "No revisions to pull" in stdout:
            return True

        # This is ok as well.
        if 'All changes applied successfully' in stderr:
            return True

        if self.strict:
            self.logger.error(
                'Error calling bazaar in "%s", detailed output follows:\n"""\n%s\n%s"""',
                branch['egg'], stdout, stderr)
            raise zc.buildout.UserError('Error calling bzr')
        else:
            # In any other case: We won't stop buildout, but we give
            # an error about the case, to notify the user.
            self.logger.error(
                'Update failed in "%s", detailed output follows:\n"""\n%% %s\n\n%s\n%s"""',
                branch['egg'], cmd, stdout, stderr)
            return

    def egg_develop(self, branch):
        develop = self.options['develop'].capitalize() == 'True'
        if not develop:
            return
        zc.buildout.easy_install.develop(branch['path'],
            self.options['develop-eggs-directory'],
            )
        self.logger.info("Develop: '%s'",
            branch['repo'])
