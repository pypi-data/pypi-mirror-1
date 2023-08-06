# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.scriptgen
"""
from setuptools import setup, find_packages


f = open('README.txt')
readme = f.read()
f.close()

version = '0.1'

entry_point = 'collective.recipe.scriptgen:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

setup(name='collective.recipe.scriptgen',
      version=version,
      description="zc.buildout recipe for generating a script",
      long_description=readme,
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://svn.plone.org/svn/collective/buildout/collective.recipe.scriptgen',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'],
      entry_points=entry_points,
      )
