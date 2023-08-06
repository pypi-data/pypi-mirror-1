from ez_setup import use_setuptools
use_setuptools()

import sys
sys.path.append('src')

from setuptools import setup
from clue.relmgr import __version__


def file_content(filename):
    f = open(filename)
    s = [x.rstrip() for x in f if x.strip() != ';-*-rst-*-']
    f.close()
    return '\n'.join(s)

readme = file_content('README.txt')
history = file_content('HISTORY.txt')

setup(name='ClueReleaseManager',
      version=__version__,
      description="An implementation of the PyPi server",
      long_description=readme + "\n" + history,
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='https://dev.serverzen.com/svn/cluemapper',
      license='BSD',
      package_dir={'': 'src'},
      packages=['clue'],
      include_package_data=True,
      zip_safe=False,
      test_suite="clue.relmgr.tests.test_suite",
      install_requires=[
          'setuptools',
          'WebOb >= 0.9.4, <= 0.9.999',
          'SQLAlchemy >= 0.5rc4',
          'repoze.who >= 1.0.8, <= 1.0.999',
          ],
      entry_points={
          'console_scripts': [
              'cluerelmgr-server = clue.relmgr.main:main',
              ],
          },
      )
