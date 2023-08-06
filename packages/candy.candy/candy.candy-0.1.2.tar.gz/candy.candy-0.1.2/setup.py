from setuptools import setup, find_packages
import os

version = '0.1.2'

setup(name='candy.candy',
      version=version,
      description="Grabs videos from youtube",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='youtube candycandy pwnyoutube',
      author='Massimo Azzolini',
      author_email='massimo.azzolini@gmail.com',
      url='http://candy-candy.googlecode.com/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['candy'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'BeautifulSoup',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
