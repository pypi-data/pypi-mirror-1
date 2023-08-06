from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

version = '0.6.1'


def file_content(filename):
    f = open(filename)
    s = [x.rstrip() for x in f if x.strip() != ';-*-rst-*-']
    f.close()
    return '\n'.join(s)

readme = file_content('README.txt')
history = file_content('HISTORY.txt')

setup(name='ClueMapperTools',
      version=version,
      description="Common tools used by ClueMapper",
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
      packages=['clue', 'clue.tools'],
      package_dir={'': 'src'},
      namespace_packages=['clue'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
      ],
      test_suite="clue.tools.tests.test_suite",
      )
