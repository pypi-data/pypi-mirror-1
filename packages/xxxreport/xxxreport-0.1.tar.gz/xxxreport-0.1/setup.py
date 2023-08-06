from setuptools import setup, find_packages
import sys, os

import re

v = open(os.path.join(os.path.dirname(__file__), 'xxxreport', '__init__.py'))
version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
v.close()

setup(name='xxxreport',
      version=version,
      description="xxxreport tools extract all TODO/XXX ... comments in a python source source",
      long_description="""\
`xxxreport` is a tools to extract all TODO/XXX comments to generate one plain text or html summary document.

`xxxreport` is inspired by Zope xxxreport tools (http://svn.zope.org/Zope3/trunk/utilities/).

How to use :

::

    $ easy_install xxxreport

Extract comments :

::

    $ xxxreport --title=WsgiDAV ~/my_python_projects/
    ===================================
    TODO/XXX Comment report for WsgiDAV
    ===================================


    Generated on Sun, 01 Nov 2009 19:27:33 CET

    Summary
    =======

    There are currently 3 TODO/XXX comments.

    Listing
    =======

    File : wsgidav/addons/virtual_dav_provider.py:220

            # TODO: this is just for demonstration:
            self.resourceData = _resourceData



    File : wsgidav/addons/virtual_dav_provider.py:350

    #            dict["etag"] = util.getETag(file path), # TODO: should be using the file path here
                dict["contentType"] = res.getContentType()
                dict["contentLength"] = res.getContentLength()
                dict["supportRanges"] = True

    File : wsgidav/addons/mysql_dav_provider.py:335

            # TODO: calling exists() makes directory browsing VERY slow.
            #       At least compared to PyFileServer, which simply used string 
            #       functions to get displayType and displayRemarks  
            if not self.exists(path):


More information :

::

    $ xxxreport --help

""",
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
