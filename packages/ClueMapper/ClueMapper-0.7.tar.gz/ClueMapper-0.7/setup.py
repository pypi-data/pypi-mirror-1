from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

version = '0.7'


def file_content(filename):
    f = open(filename)
    s = [x.rstrip() for x in f]
    f.close()
    return '\n'.join(s)

readme = file_content('README.txt')
history = file_content('HISTORY.txt')

setup(name='ClueMapper',
      version=version,
      description="A web-based application for managing software projects.",
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
      packages=['clue', 'clue.app'],
      package_dir={'': 'src'},
      namespace_packages=['clue'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools >= 0.6c8',
          'Paste >= 1.7, <= 1.7.9999',

          # ClueMapper
          'ClueMapperChatter >= 0.6',
          'ClueMapperThemer >= 0.6.3',
          'ClueMapperTools >= 0.6.1',
          'ClueMapperSecure >= 0.6.3',

          # ClueMapper uses ClueBin's sql support which is optional for cluebin
          'ClueBin >= 0.2.3',
          'SQLAlchemy >= 0.4.6, <= 0.4.9999',

          # Trac and deps
          'Trac >= 0.11, <= 0.11.9999',
          'Genshi >= 0.5, <= 0.5.9999',
          'repoze.trac >= 0.6, <= 0.6.9999',
          'Pygments >= 0.10, <= 0.10.9999',
          'pytz >= 2008b',
          'docutils >= 0.4, <= 0.4.9999',
          'pysqlite >= 2.4.1, <= 2.4.9999',

          # Bitten continous build integration
          'Bitten >= 0.5',
          'clearsilver >= 0.10.1',

          # various extra Trac plugins required
          'timingandestimationplugin',
          'TracTags',
          'TracWebAdmin',
          'TracCustomFieldAdmin',
          'TracIncludeMacro',
          'TracWysiwyg',
          ],
      test_suite="clue.app.tests.test_suite",
      entry_points={
          'trac.plugins': [
              'ClueMapper Plugins = clue.app.tracplugins',
              ],
          'console_scripts': [
              'clue-server = clue.app.server:main',
              'clue-admin = clue.app.admin:main',
              ]},
      )
