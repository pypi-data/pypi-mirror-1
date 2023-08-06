from setuptools import setup, find_packages
import os

version = '1.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name = 'gf.recipe.bzr',
    version = version,
    description = "Buildout recipe to download bazaar branches",
    long_description = read('docs', 'README.txt'),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords = '',
    author = 'Balazs Ree',
    author_email='ree@greenfinity.hu',
    url='',
    license = 'GPL',
    packages = find_packages(exclude=['ez_setup']),
    namespace_packages = ['gf.recipe'],
    include_package_data = True,
    #zip_safe = False,
    install_requires = {
          'setuptools': ['setuptools'],
          'bzr': ['bzr'],
    },
    entry_points = {
        'zc.buildout': ['default = gf.recipe.bzr.bzr:BzrRecipe'],
        'zc.buildout.uninstall': ['default = gf.recipe.bzr.bzr:uninstallBzrRecipe'],
    },
)
