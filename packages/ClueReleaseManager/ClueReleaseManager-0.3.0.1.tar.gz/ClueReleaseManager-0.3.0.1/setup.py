from ez_setup import use_setuptools
use_setuptools()

import sys
sys.path.insert(0, 'src')

from setuptools import setup
from clue.relmgr import __version__

readme = open('README.txt').read().strip()
history = open('HISTORY.txt').read().strip()

url = 'http://projects.serverzen.com/pm/p/cluemapper/ClueReleaseManager'

setup(name='ClueReleaseManager',
      version=__version__,
      description="An implementation of a PyPi server",
      long_description=readme + "\n" + history,
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url=url,
      license='BSD',
      package_dir={'': 'src'},
      packages=['clue'],
      include_package_data=True,
      zip_safe=False,
      test_suite="clue.relmgr.tests.test_suite",
      install_requires=[
          'setuptools',
          'SQLAlchemy >= 0.5',
          'repoze.who >= 1.0.8, <= 1.0.999',
          'Werkzeug >= 0.4',
          'Jinja2 >= 2.1',
          'docutils >= 0.5',
          ],
      entry_points={
          'console_scripts': [
              'cluerelmgr-server = clue.relmgr.main:main',
              'cluerelmgr-admin = clue.relmgr.cmdtool:main',
              ],
          },
      )
