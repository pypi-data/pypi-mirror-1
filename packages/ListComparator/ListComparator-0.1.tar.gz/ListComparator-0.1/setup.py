from setuptools import setup, find_packages
import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    '\n.. contents::\n\n' +
    'Detailed Documentation\n' +
    '**********************\n'
    + '\n' +
    read('README.txt')
    + '\n\n' +
    'Contributors\n' +
    '************\n'
    + '\n' +
    read('Contributors.txt')
    + '\n' +
    'Change history\n' +
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )

setup(name='ListComparator',
      version=version,
      description="Compares ordered lists, xml and csv application",
      long_description=long_description,
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
                   'Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Text Processing :: Filters',
                   'Topic :: Text Processing :: Markup :: XML',
                   'Topic :: Utilities',
                   ],
      keywords='xml csv list compare diff difference',
      author='Nicolas Laurance',
      author_email='nlaurance at zindep dot com',
      url='http://code.google.com/p/listcomparator/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'elementtree',
      ],
      tests_require=[
          'nose',
      ],
    entry_points={'console_scripts': ['csv_cmp = listcomparator.csv_cmp:main',
                                      'xml_cmp = listcomparator.xml_cmp:main']},
    test_suite='nose.collector',
      )
