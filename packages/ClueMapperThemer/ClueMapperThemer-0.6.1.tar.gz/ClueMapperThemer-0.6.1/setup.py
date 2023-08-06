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

setup(name='ClueMapperThemer',
      version=version,
      description="Theming plugin for ClueMapper+trac.",
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
      packages=['clue', 'clue.themer'],
      package_dir={'': 'src'},
      namespace_packages=['clue'],
      include_package_data=True,
      package_data={'clue.themer': ['defaulttheme/rules/*',
                                    'defaulttheme/static/*']},
      zip_safe=True,
      install_requires=[
          'setuptools',
          'Deliverance',
          'lxml >= 2.0.4, <= 2.0.9999',
          'Paste >= 1.6, <= 1.6.9999',
      ],
      entry_points="",
      test_suite="clue.themer.tests.test_suite",
      )
