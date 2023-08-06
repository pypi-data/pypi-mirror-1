from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

description = """geomobilejp is utilities to handle GPS infomation of Japanese mobile devices"""

setup(name='geomobilejp',
      version=version,
      description="PyGeoMobileJP",
      long_description=description,
      classifiers=filter(None, map(str.strip, """\
Development Status :: 4 - Beta
License :: OSI Approved :: MIT License
Programming Language :: Python
Operating System :: OS Independent
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines())),
      keywords='',
      author='Chihio Sakatoku',
      author_email='csakatoku@mac.com',
      url='http://code.google.com/p/pygeomobilejp/',
      license='MIT License',
      platforms=["any"],
      packages=find_packages(exclude=['examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite='nose.collector'
      )
