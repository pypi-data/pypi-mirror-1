from setuptools import setup, find_packages
import os

version = '1.0b1'

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'HISTORY.txt')).read()
except IOError:
    README = CHANGES = ''


setup(name='qc.statusmessage',
      version=version,
      description="WSGI Middleware for displaying status messages",
      long_description=README + '\n\n' +  CHANGES,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware", 
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",

        ],
      keywords='statusmessage quantumcore wsgi middleware web framework',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://quantumcore.net',
      license='BSD License, http://quantumcore.org/license.html',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['qc'],
      zip_safe=False,
      test_suite="qc.statusmessage.tests",
      include_package_data=True,
      install_requires=[
          'setuptools',
          'paste',
          'simplejson',
          # -*- Extra requirements: -*-
      ],
      entry_points="""\
      [paste.filter_app_factory]
      middleware = qc.statusmessage.middleware:make_statusmessage_middleware
      """,
      )
