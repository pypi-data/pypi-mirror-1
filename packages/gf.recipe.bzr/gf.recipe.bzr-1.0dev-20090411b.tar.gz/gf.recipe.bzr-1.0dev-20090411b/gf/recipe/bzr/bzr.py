
import logging, os, sys, zc.buildout, subprocess, re


if sys.platform == 'win32':
    BZR = 'bzr.bat'
else:
    BZR = 'bzr'

import shutil

def execute(cmd, logger):
    logger.debug('Calling bazaar in %s:\n  %s', 
        os.getcwd(), cmd)
    # Feed it a bunch of newlines, in case it asks for password
    # (if you use password authentication, install pycurl
    # and specify the newlines in .netrc
    proc = subprocess.Popen(cmd.split(),
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
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

re_extra_rev = re.compile(r'(^|\n)You have \d+ extra revision\(s\):')
re_push_location = re.compile(r'push branch: ([^\n]*)\n')
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

    For more information, consult the file docs/README.txt in the egg.
    """

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.setup_logging()
        in_parts = options.get('in_parts', 'False')
        if in_parts not in ('True', 'False', 'true', 'false'):
            self.logger.error(
                'Bad in_parts parameter "%s", allowed values: True or False',
                in_parts)
            raise zc.buildout.UserError('Bad in_parts parameter')
        options['develop'] = develop = options.get('develop', 'True')
        if develop not in ('True', 'False', 'true', 'false'):
            self.logger.error(
                'Bad develop parameter "%s", allowed values: True or False',
                develop)
            raise zc.buildout.UserError('Bad develop parameter')

        root_dir = buildout['buildout']['directory']
        if in_parts.capitalize() == 'True':
            root_dir =  os.path.join(root_dir, 'parts')
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
                #
                branches.append(dict(
                    egg = egg, 
                    repo = repo,
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
            os.mkdir(root_dir)

        # process required branches
        for branch in self.branches:
            if not os.path.isdir(branch['path']):
                # this is not possible in offline mode
                if self.buildout['buildout'].get('offline', '').lower() == 'true':
                    self.logger.error('Cannot get %s from bzr repository %s,' +
                        ' in offline mode.', branch['egg'], branch['repo'])
                    raise zc.buildout.UserError('Cannot use bzr in offline mode')
                self.logger.info('Getting %s from bzr repository %s',
                    branch['egg'], branch['repo'])
                self.bzr_get(branch)
            else:
                # Only update in online mode
                if self.buildout['buildout'].get('offline', '').lower() != 'true':
                    self.bzr_update(branch)
            # setup.py develop the egg.
            self.egg_develop(branch)

        # XXX Never uninstall anything.
        # However checks are done ans uninstall is aborted
        # in case there are pending changes, but still
        # we don't delete anything, really.
        return []

    def update(self):
        # No updates when offline
        if self.buildout['buildout'].get('offline', '').lower() == 'true':
            return 
        self.install()

    def bzr_get(self, branch):

        # Getting by calling bazaar
        cmd = BZR + ' get %(repo)s %(path)s' % branch
        stdout, stderr = self.execute(cmd)

        # check for errors
        # stderr may be multi line, we check last line
        stderr_lines = stderr.splitlines()
        if not stderr_lines or not stderr_lines[-1].startswith('Branched'):
            self.logger.error(
                'Error calling bazaar in "%s", detailed output follows:\n"""\n%s\n%s"""',
                branch['egg'], stdout, stderr)
            raise zc.buildout.UserError('Error calling bzr')

        try:
            # Do the pull now, just to remember the location
            cmd = 'bzr pull --remember %(repo)s' % branch
            self.bzr_pull(cmd, branch)
        except zc.buildout.UserError:
            # remove the branch, actually
            shutil.rmtree(branch['path'], ignore_errors=True)
            raise

    def bzr_update(self, branch):
        # Updating by calling bazaar
        os.chdir(branch['path'])

        # We need to acquire the pull location,
        # mainly because we may want to add the password to it.
        cmd = BZR + ' info'
        stdout, stderr = self.execute(cmd)
        match = re_pull_location.search(stdout)
        if stderr or match is None:
            self.logger.error(
                'Abort uninstalling "%s" (not a bzr branch, or no pull location?), detailed bzr output follows:\n"""\n%s\n%s"""',
                branch['egg'], stdout, stderr)
            raise zc.buildout.UserError('Error calling bzr')
        location = match.group(1)

        # Add password (if any) to location
        location = add_password(self.options, location)

        # Do the pull now
        cmd = '%s pull %s' % (BZR, location)
        self.bzr_pull(cmd, branch)

    def bzr_pull(self, cmd, branch):

        os.chdir(branch['path'])

        stdout, stderr = self.execute(cmd)

        # check for errors

        # This is ok.
        if "No revisions to pull" in stdout:
            return
    
        # This is ok as well.
        if 'All changes applied successfully' in stderr:
            return

        # In any other case: We won't stop buildout, but we give
        # an error about the case, to notify the user.
        self.logger.error(
            'Update failed in "%s", detailed output follows:\n"""\n%s\n%s"""',
            branch['egg'], stdout, stderr)
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
