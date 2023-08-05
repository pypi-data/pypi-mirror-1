from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(name='flexable',
      version=version,
      description="Template engine with simple data structure",
      long_description="""`flexable` is template engine with simple data structure.
That is made up of str, unicode, dict, tuple, list and Element.

""",
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Text Processing ',
                   'Topic :: Text Processing :: Markup :: HTML',
                   'Topic :: Text Processing :: Markup :: XML'
                   ],
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='wsgi template xml',
      author='Atsushi Odagiri',
      author_email='aodagx@gmail.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
        "lxml"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
