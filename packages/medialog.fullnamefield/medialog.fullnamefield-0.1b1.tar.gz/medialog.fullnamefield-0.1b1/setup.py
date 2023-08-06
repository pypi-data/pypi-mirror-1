# Copyright 2008-2009, Grieg Medialog http://medialog.no
# Free as in free beer licence

import os
from setuptools import setup, find_packages

version = '0.1b1'
shortdesc = "Archetypes Widget dealing with fullname."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
license = open(os.path.join(os.path.dirname(__file__), 'LICENSE.txt')).read()
history = open(os.path.join(os.path.dirname(__file__), 'docs/HISTORY.txt')).read()
contributors = open(os.path.join(os.path.dirname(__file__), 'docs/CONTRIBUTORS.txt')).read()

setup(name='medialog.fullnamefield',
      version=version,
      description=shortdesc,
      long_description=longdesc + history + contributors + license,
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
           ],
      keywords='plone archetypes field fullname',
      author='Espen Moe-Nilssen',
      author_email='espen@medialog.no',
      url='http://medialog.no',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['medialog'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.Archetypes',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
