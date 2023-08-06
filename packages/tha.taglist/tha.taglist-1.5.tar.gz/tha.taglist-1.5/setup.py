from setuptools import setup, find_packages
import os

version = '1.5'

setup(name='tha.taglist',
      version=version,
      description="Create find-links list of tags",
      long_description=(open("README.txt").read() + "\n\n" +
                        open("CHANGES.txt").read() + "\n\n" +
                        open("TODO.txt").read()),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='The Health Agency',
      author_email='techniek@thehealthagency.com',
      url='http://thehealthagency.com',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['tha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'tha.tagfinder >= 0.4',
          'Jinja2',
      ],
      entry_points={
          'console_scripts': ['taglist = tha.taglist.exporter:main'],
          },
      )
