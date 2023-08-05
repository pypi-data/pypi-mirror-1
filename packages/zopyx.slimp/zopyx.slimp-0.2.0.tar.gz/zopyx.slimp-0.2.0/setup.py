# zopyx.slimp - A Python wrapper for the slimserver software
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
]

version_file = os.path.join('src', 'zopyx', 'slimp', 'version.txt')
version = open(version_file).read().strip()

readme_file = os.path.join('src', 'zopyx', 'slimp', 'README.txt')
desc = open(readme_file).read() 

changes_file = os.path.join('src', 'zopyx', 'slimp', 'CHANGES.txt')
changes = open(changes_file).read()

long_description = desc + '\nChanges:\n========\n\n' + changes


setup(name='zopyx.slimp',
      version=version,
      license='ZPL (see LICENSE.txt)',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      classifiers=CLASSIFIERS,
#      url='http://svn.zope.org/zopyx.slimp/tags/%s' % version,
      description='A Python interface for the slimserver software',
      long_description=long_description,
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data = True,
      zip_safe=True,
      install_requires=['setuptools'],
      entry_points={'console_scripts': ['slimplayer = zopyx.slimp.slimplayer:main',]},
      )                       
