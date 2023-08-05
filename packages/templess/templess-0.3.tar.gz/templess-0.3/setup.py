from setuptools import setup, find_packages

version =  open('version.txt').read().strip()

long_description = open('doc/README.txt').read()

setup(name='templess',
      version=version,
      description="Templess templating system",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Internet :: WWW/HTTP',
                   ], 
      keywords="templess",
      author="Guido Wesdorp",
      author_email="johnny@johnnydebris.net",
      url="http://templess.johnnydebris.net/",
      package_dir={'templess': '.'},
      packages=['templess'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
