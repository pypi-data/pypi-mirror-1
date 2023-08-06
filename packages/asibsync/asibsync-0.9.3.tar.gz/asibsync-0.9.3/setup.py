from setuptools import setup, find_packages
import sys, os

version = '0.9.3'

setup(name='asibsync',
      version=version,
      description="ASI-SIB synchronization agent",
      long_description=open("README.txt").read() + "\n" +
                             open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[ # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.6',
          'Topic :: Internet',
      ],
      keywords='ASI Smart-M3 SIB sync',
      author='Eemeli Kantola',
      author_email='eemeli.kantola@iki.fi',
      url='http://asibsync.sourceforge.net',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
      include_package_data=True,
      zip_safe=True,
      dependency_links = [
          
      ],
      install_requires=[
          'asilib >=1.0.2',
          'kpwrapper >=1.0.2',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
