import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
    )

setup(
    name = "plone.recipe.distros",
    version = "1.5",
    author = "Hanno Schlichting",
    author_email = "hannosch@plone.org",
    description = "ZC Buildout recipe for installing distributions.",
    long_description=long_description,
    license = "ZPL 2.1",
    keywords = "buildout",
    url='http://pypi.python.org/pypi/plone.recipe.distros',
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Plone",
      "Framework :: Buildout",
      "Programming Language :: Python",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['plone', 'plone.recipe'],
    install_requires = ['zc.buildout', 'setuptools'],
    entry_points = {'zc.buildout': ['default = plone.recipe.distros:Recipe']},
    )
