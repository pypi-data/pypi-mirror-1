from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='WSGIProfile',
      version=version,
      description="WSGI Middleware for embedding a rich profiler in web pages.",
      long_description="""\
""",
      classifiers=['Topic :: Software Development :: Debuggers',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX'],
      keywords='profile profiling wsgi middleware',
      author='Stephen Emslie',
      author_email='stephenemslie@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'webob',
          'paste',
          'routes',
          'mako'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
