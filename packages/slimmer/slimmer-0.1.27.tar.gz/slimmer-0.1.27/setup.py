from setuptools import setup, find_packages
import sys, os

version = '0.1.27'

setup(name='slimmer',
      version=version,
      description="HTML,XHTML,CSS,JavaScript optimizer",
      long_description="""\
slimmer.py
---------------------

Can slim (X)HTML, CSS and Javascript files to become smaller""",
      keywords='slimmer optimizer optimiser whitespace',
      author='Peter Bengtsson',
      author_email='peter@fry-it.com',
      url='http://www.fry-it.com',
      license='Python',
      classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Other/Nonlisted Topic",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],      
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      test_suite='slimmer.tests',
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
