from setuptools import setup, find_packages
import os

version = '1.0'

def read(rnames):
    setupdir =  os.path.dirname( os.path.abspath(__file__))
    return open(
        os.path.join(setupdir, *rnames)
    ).read()

README =read((os.path.dirname(__file__),'README.txt')) +\
        read((os.path.dirname(__file__),
              'src', 'ClueReleaseManager', 'paste','paste',
              'docs', 'README.txt'))
CHANGELOG  = read((os.path.dirname(__file__),
                      'docs', 'HISTORY.txt'))
TESTS  = read((os.path.dirname(__file__),
               'src', 'ClueReleaseManager', 'paste','paste',
               'doctests', 'README.txt'))
long_description = '\n'.join([README, TESTS,CHANGELOG])+'\n\n'
setup(name='ClueReleaseManager.paste',
      version=version,
      description="Yet another WSGI Paste factory for paste and ClueReleaseManager",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Mathieu Pasquet',
      author_email='kiorky@cryptelium.net',
      url='http://git.minitage.org/git/others/ClueReleaseManager.paste',
      license='GPL',
      namespace_packages=['ClueReleaseManager', 'ClueReleaseManager.paste'],
      include_package_data=True,
      zip_safe=False,
      packages=find_packages('src'),
      extras_require={'test': ['ipython', 'zope.testing', ]},
      package_dir = {'': 'src'},
      install_requires=[
          'setuptools',
          'WebOb',
          'Werkzeug',
          'PasteScript',
          'ClueReleaseManager',
      ],
      entry_points={
          'paste.app_factory': ['main=ClueReleaseManager.paste.paste:crmgr_factory',
                               ],
      },
     )
