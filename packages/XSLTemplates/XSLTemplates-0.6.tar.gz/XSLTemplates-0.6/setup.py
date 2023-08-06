from setuptools import setup, find_packages
import sys, os
from setuptools import setup, find_packages
import sys, os

version = '0.6'

setup(name='XSLTemplates',
      version=version,
      description="An XSLT based template system for WSGI applications.",
      long_description="""\
XSLTemplate is a simple XSLT based templating system that was created in order to use XSLT for WSGI web applications. The goal is to have a simple means of using XSLT for templating as well as provide an obvious and simple way of extending template via traditional XSLT extension functions and elements.

As it is based on 4Suite, all the 4Suite documentation can be used as a basis for creating extensions. Also, XSLTemplate comes with some basic extensions specific to web applications.
""",
      classifiers=[
          'Environment :: Web Environment',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing :: Markup :: HTML',
          'Topic :: Text Processing :: Markup :: XML',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware'
          ],
      keywords='xml xslt wsgi template',
      author='Eric Larson',
      author_email='eric@ionrock.org',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Amara>=1.2',
          'wsgixml>=0.3',
      ],
      )
