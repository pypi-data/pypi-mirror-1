from setuptools import setup, find_packages

version = '0.1'


def file_content(filename):
    f = open(filename)
    s = [x.rstrip() for x in f]
    f.close()
    return '\n'.join(s)

readme = file_content('README.txt')
history = file_content('HISTORY.txt')

setup(name='ClueBzrServer',
      version=version,
      description="A simple bzr server",
      long_description=readme + "\n" + history,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['clue'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'repoze.who >= 1.0.7, <= 1.0.999',
          'bzr >= 1.9',
      ],
      entry_points={
          'console_scripts': [
              'clue-bzrserver = clue.bzrserver.main:main',
              ],
          },
      )
