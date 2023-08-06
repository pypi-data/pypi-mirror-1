from __future__ import with_statement
from setuptools import setup, find_packages

version = '0.2'


with open('README.txt') as f:
    readme = f.read().strip()
with open('HISTORY.txt') as f:
    history = f.read().strip()

setup(name='ClueBzrServer',
      version=version,
      description=("A standalone server application for serving "
                   "up Bazaar repositories over HTTP"),
      long_description=readme + "\n\n" + history,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: Version Control',
        ],
      keywords='bzr bazaar repoze.who dvcs',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://projects.serverzen.com/pm/p/cluemapper/wiki/ClueBzrServer',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['clue'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools >= 0.6c9',
          'repoze.who >= 1.0.10',
          'bzr >= 1.12',
          'Paste >= 1.7.2',
      ],
      entry_points={
          'console_scripts': [
              'clue-bzrserver = clue.bzrserver.main:main',
              ],
          },
      )
