from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='OHM',
      version=version,
      description="Object HTTP Mapper",
      long_description="""\
The Object HTTP Mapper provides tools both to expose your objects as
WSGI applications, and to create objects with attributes that delegate
to web requests.

Objects are generally containers, with attributes as resources in
those containers.  The resources are not homogenous -- one might be a
JSON object, another XML, another a string.  HTTP methods (``GET``,
``PUT``, ``DELETE``) are used to get, set, and delete attributes.

This project is in a `subversion repository
<http://svn.pythonpaste.org/Paste/OHM/trunk#egg=OHM-dev>`_ and the
development version can be installed with ``easy_install OHM==dev``.
Interested users should probably follow the development.
""",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
      ],
      keywords='wsgi web http metaprogramming',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='http://pythonpaste.org/ohm/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'simplejson',
        'Paste',
        'FormEncode',
        'HTTPEncode',
      ],
      #entry_points="""
      #""",
      )
      
