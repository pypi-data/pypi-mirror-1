import os
from setuptools import setup, find_packages

name = "osc.recipe.sysegg"
version = '0.1.1'

setup(
    name = name,
    version = version,
    author = "Oliver Tonnhofer",
    author_email = "olt@omniscale.de",
    description = 'zc buildout recipe to reuse eggs from python site-packages.',
    long_description=open('README.txt').read() +'\n' + open('CHANGELOG.txt').read(),
    license = 'MIT License',
    classifiers=[
      'License :: OSI Approved :: MIT License',
      'Framework :: Buildout',
      'Programming Language :: Python',
      ],

    packages = find_packages(),
    zip_safe = False,
    namespace_packages = ['osc', 'osc.recipe'],
    install_requires = ['zc.buildout', 'setuptools'],
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
)
