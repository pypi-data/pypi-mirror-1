==============================
gf.recipe.bzr buildout recipee
==============================

This recipe can be used to get development checkouts from Bazaar repositories
for zc.buildout.

Installation and Setup
======================

Read INSTALL.txt


Documentation
=============

Goals
-----

- Allow fetching eggs directly from bzr repositories.

- The specified repositories are branched locally on the first buildout run. It
  is possible to use these local branches for development and make local
  changes. The local changes can be committed locally, and can be pushed back
  to the remote repository or to any other location.

- When buildout is run again, the branches are updated (pulled) automatically
  from the remote location. If pulling would cause conflicts, buildout stops
  with an error. The parent branch (pull) location remembered by bazaar will be
  used for pulling, so it is possible to change this any time from bzr.

- Local changes can be pushed back to the remote branches. This is also enforced:
  When buildout wants to uninstall the local branches, they are checked. If
  they contain uncommitted or unpushed local changes, buildout stops with an
  error. This forces developers to save local changes to upstream and avoids
  loosing local work.

- When buildout checks if the branches contain local changes, the parent (pull)
  location and the push location, remembered by bazaar, are used (in this
  order). This makes it possible to switch existing branches during
  development, without changing the buildout configuration.

- Parameters are similar to those used with "infrae.subversion" and also
  compatible with the "bazaarrecipe" package.

- With bzr-svn, the remote branch can also be an svn branch. So it actually can
  be used to branch off native svn repository branches as well (although,
  performance of updates and sanity checks may depend on bzr-svn's performance,
  thus infrae.subversion may provide faster operation for svn.)


Usage
-----

Usage example::
        
    [bzr]
    recipe = gf.recipe.bzr
    urls =
        http://bazaar.launchpad.net/~kissbooth/kss.plugin.sdnd/trunk kss.plugin.sdnd 
        http://bazaar.launchpad.net/~kissbooth/kss.plugin.livesearch/trunk kss.plugin.livesearch
    in_parts = False
    http_authentication = username:password

This will ``bzr get`` the branches to ``bzr/kss.plugin.sdnd`` and
``bzr/kss.plugin.livesearch``.  Branches are pulled if buildout is called.
Uninstall is protected, if there are local modifications, or modifications that
are missing in the upstream, an error will be raised. In case you create a
local bzr directory, make sure it has a push location, otherwise uninstall will
fail.

No directories are really removed on uninstall, this has the consequence that
if the setup is changed, the local repositories will not follow it.

The ``in_parts`` option
"""""""""""""""""""""""

``in_parts`` is by default false, which means the directory that holds the branches
is created in the buildout root. This is the default mode as it is handy for
development. If in_parts = True is specified, then the directory will be
created in the parts directory (compatible with infrae.subversion).

The ``http_authentication`` option
""""""""""""""""""""""""""""""""""

If ``http authentication`` is specified as ``username:password``, it will be used for
authenticating into http and https realms. This is rarely needed as ssh offers
a more confortable repository access, but it allows password protected http
access that would not be easy (or possible at all) otherwise.

The option is inactive with ``bzr+ssh://`` repository urls.

The ``develop`` option
""""""""""""""""""""""

The branches fetched by the recipe are also installed as development eggs, by
default. The ``develop = False`` option can be used to force the recipe not to
develop the eggs. This can be useful, for example, to use buildout to update
local read-only bazaar mirrors of an svn repository::

    [kukit.js]
    recipe = gf.recipe.bzr
    urls=
        https://codespeak.net/svn/kukit/kukit.js/trunk              trunk
        https://codespeak.net/svn/kukit/kukit.js/branch/1.2         1.2
        https://codespeak.net/svn/kukit/kukit.js/branch/1.4         1.4
    develop = False

    [kss.demo]
    recipe = gf.recipe.bzr
    urls=
        https://codespeak.net/svn/kukit/kss.demo/trunk              trunk
        https://codespeak.net/svn/kukit/kss.demo/branch/1.2         1.2
        https://codespeak.net/svn/kukit/kss.demo/branch/1.4         1.4
    develop = False


Offline mode is not supported for uninstalls
""""""""""""""""""""""""""""""""""""""""""""

Offline mode is *not* supported for uninstalls, because there seems 
to be no way of detecting during uninstall, if we are in offline mode.

This means that if you run buildout in offline mode, and buildout decides that
an uninstall is needed, the recipe will still attempt an online connection
to the upstream repository. If this gets you into a deadlock, you need to
run buildout in online mode, or remove your branches manually if you choose to
resolve the situation by loosing all your local changes.


Other configuration needed
--------------------------

In addition you also need to include the eggs you configured with the recipe,
in the buildout section::

    [buildout]
    ...
    eggs =
        ...
        kss.plugin.sdnd
        kss.plugin.livesearch


