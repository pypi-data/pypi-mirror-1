from setuptools import setup

import os

def read(*filenames):
    return open(os.path.join(os.path.dirname(__file__), *filenames)).read()

setup(name = 'cashflow',
      version = '1.0',
      description = 'Reads a Gnucash file and computes your cash flow',
      long_description = read('src/cashflow/README.txt'),
      license = 'GPL',
      author = 'Brandon Craig Rhodes',
      author_email = 'brandon@rhodesmill.org',
      classifiers = [
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'Environment :: Console',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Accounting',
        ],
      packages = [ 'cashflow' ],
      package_dir = { '': 'src' },
      test_suite = 'cashflow.tests',
      entry_points = {
        'console_scripts': [
            'cashflow = cashflow.command:main',
            ],
        },
      )
