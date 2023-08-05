import os
from setuptools import setup, find_packages

name = "affinitic.recipe.fakezope2eggs"
version = '0.3'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = name,
    version = version,
    author = "Jean-Francois Roche",
    author_email = "jfroche@affinitic.be",
    description = "ZC Buildout recipe to fake zope 2 packages as eggs.",
    long_description=(read('README.txt')),
    license = "ZPL 2.1",
    keywords = "zope2 buildout",
    url='http://svn.affinitic.be/zope/affinitic.recipe.fakezope2eggs',
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      "Framework :: Plone",
      "Framework :: Zope2",
      "Programming Language :: Python",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    zip_safe = False,
    namespace_packages = ['affinitic', 'affinitic.recipe'],
    install_requires = ['zc.buildout', 'setuptools',
                        'plone.recipe.zope2install'],
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )

