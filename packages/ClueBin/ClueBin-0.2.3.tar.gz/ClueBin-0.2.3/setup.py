from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

version = '0.2.3'


def file_content(filename):
    f = open(filename)
    s = [x.rstrip() for x in f]
    f.close()
    return '\n'.join(s)

readme = file_content('README.txt')
history = file_content('HISTORY.txt')

setup(name='ClueBin',
      version=version,
      description="Pastebin application",
      long_description=readme + "\n" + history,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='',
      license='',
      packages=['cluebin'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      test_suite="cluebin.tests.test_suite",
      install_requires=[
          'Pygments >= 0.9',
          'WebOb >= 0.9.1',
      ],
      entry_points={
          'console_scripts': [
              'cluebin = cluebin.pastebin:main',
              ]},
      )
