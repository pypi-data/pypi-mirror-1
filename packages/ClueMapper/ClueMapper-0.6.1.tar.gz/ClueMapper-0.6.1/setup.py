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
          'setuptools',
          'Paste >= 1.6, <= 1.6.9999',

          # ClueMapper
          'ClueMapperChatter',
          'ClueMapperThemer',
          'ClueMapperTools',
          'ClueMapperSecure',

          # controller uses cluebin's sql support which is optional for cluebin
          'ClueBin',
          'SQLAlchemy >= 0.4.6, <= 0.4.9999',

          # Trac and deps
          'Trac >= 0.11rc1, <= 0.11.9999',
          'repoze.trac >= 0.6, <= 0.6.9999',
          'Genshi >= 0.5dev',
          'Pygments >= 0.9, <= 0.9.9999',
          'pytz == 2007k',
          'docutils >= 0.4, <= 0.4.9999',
          'pysqlite >= 2.4.1, <= 2.4.9999',

          # various extra Trac plugins required
          'timingandestimationplugin',
          'TracTags',
          'TracWebAdmin',
          'TracCustomFieldAdmin',
          ],
      test_suite="clue.app.tests.test_suite",
      entry_points={
          'trac.plugins': [
              'ClueMapper Themes = clue.app.tracplugins',
              ],
          'console_scripts': [
              'clue-server = clue.app.server:main',
              'clue-admin = clue.app.admin:main',
              ]},
      )
