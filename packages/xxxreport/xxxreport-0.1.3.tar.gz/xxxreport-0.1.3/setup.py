from setuptools import setup, find_packages
import sys, os
import re

here = os.path.abspath(os.path.dirname(__file__))

v = open(os.path.join(here, 'xxxreport', '__init__.py'))
version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
v.close()

try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

setup(name='xxxreport',
      version=version,
      description="xxxreport tools extract all TODO/XXX ... comments in a python source source",
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        'Intended Audience :: Developers', 
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Documentation',
        'Topic :: Terminals'
      ],
      keywords='comments, extract, TODO',
      author='Stephane Klein',
      author_email='stephane@harobed.org',
      url='http://code.google.com/p/xxxreport/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'console_scripts': [
            "xxxreport = xxxreport.main:main",
        ]
      },
      )
