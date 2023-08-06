from setuptools import setup, find_packages
import sys, os

version = '1.0.2'

setup(name='asiconsole',
      version=version,
      description="Python ASI console for interactive testing and debugging",
      long_description=open("README.txt").read() + "\n" +
                             open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[ # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Intended Audience :: Developers',
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Programming Language :: Python :: 2.6',
          'Topic :: Internet',
      ],
      keywords='ASI REST OtaSizzle console',
      author='Eemeli Kantola',
      author_email='eemeli.kantola@iki.fi',
      url='http://asibsync.sourceforge.net',
      license='BSD',
      py_modules=['asiconsole'],
      include_package_data=True, # process MANIFEST.in
      zip_safe=True,
      dependency_links = [
          
      ],
      install_requires=[
          'ipython',
          'asilib >=1.0.2',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
