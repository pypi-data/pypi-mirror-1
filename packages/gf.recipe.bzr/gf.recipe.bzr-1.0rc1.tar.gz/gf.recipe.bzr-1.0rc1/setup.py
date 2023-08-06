from setuptools import setup, find_packages
import os

version = '1.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'gf.recipe.bzr',
    version = version,
    description = "Buildout recipe to download bazaar branches",
    long_description = (
        read('docs', 'README.txt')
        + '\n' +
        'Recent changes\n'
        '==========================\n' +
        read('docs', 'HISTORY.txt')
        + '\n' +
        'Download\n'
        '==========================\n'
        ),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords = '',
    author = 'Balazs Ree',
    author_email = 'ree@greenfinity.hu',
    url = 'http://launchpad.net/gf.recipe.bzr',
    license = 'GPL',
    packages = find_packages(exclude=['ez_setup']),
    namespace_packages = ['gf', 'gf.recipe'],
    include_package_data = True,
    zip_safe = True,
    install_requires = {
          'setuptools': ['setuptools'],
    },
    entry_points = {
        'zc.buildout': [
            'default = gf.recipe.bzr.bzr:BzrRecipe',
            'strict = gf.recipe.bzr.bzr_strict:BzrRecipe',
            ],
        'zc.buildout.uninstall': [
            'strict = gf.recipe.bzr.bzr_strict:uninstallBzrRecipe',
            ],
    },
)
