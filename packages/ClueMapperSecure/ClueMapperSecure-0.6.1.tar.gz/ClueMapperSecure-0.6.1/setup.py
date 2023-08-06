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

setup(name='ClueMapperSecure',
      version=version,
      description="Security component for ClueMapper.",
      long_description=readme + "\n" + history,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://projects.serverzen.com/pm/p/cluemapper',
      license='BSD',
      packages=['clue', 'clue.secure'],
      package_dir={'': 'src'},
      namespace_packages=['clue'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'Paste >= 1.6, <= 1.6.9999',
          'repoze.who >= 1.0.1, <= 1.0.9999',
          'TracUserManagerPlugin',
          'TracAccountManager',
          'TracCustomFieldAdmin',
      ],
      entry_points="",
      test_suite="clue.secure.tests.test_suite",
      )
