from setuptools import setup, find_packages
import sys, os

version = '1.0.2'

tests_require = ['minimock']

setup(name='asilib',
      version=version,
      description="Aalto Social Interface (ASI) Python interface library",
      long_description=open("README.txt").read() + "\n" +
                             open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[ # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2.6',
          'Topic :: Internet',
      ],
      keywords='ASI REST OtaSizzle',
      author='Eemeli Kantola',
      author_email='eemeli.kantola@iki.fi',
      url='http://asibsync.sourceforge.net',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
      include_package_data=True, # process MANIFEST.in
      zip_safe=True,
      dependency_links = [
          'http://public.futurice.com/~ekan/eggs',
      ],
      install_requires=[
          'restlib >=0.9',
          'opensocial.py',
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
