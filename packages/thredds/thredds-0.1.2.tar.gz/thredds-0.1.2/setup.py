RELEASE = True

from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.1.2'

setup(name='thredds',
      version=version,
      description="THREDDS catalog generator.",
      long_description="""\
This is a THREDDS catalog generator implemented as a WSGI application.

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/thredds#egg=thredds-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='thredds data',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://pydap.org/related/thredds.html',
      download_url = "http://cheeseshop.python.org/packages/source/t/thredds/thredds-%s.tar.gz" % version,
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'Paste',
      ],
      extras_require={
          'dap': ['dap[server]>=2.2.5.1'],
      },
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = thredds.application:make_app
      """,
      )
      
