from setuptools import setup, find_packages
import os

version_file = os.path.join('collective', 'transform', 'docbook', 'version.txt')
version = open(version_file).read().strip()

setup(name='collective.transform.docbook',
      version=version,
      description="DocBook text transform for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Timo Stollenwerk',
      author_email='timo@zmag.de',
      url='https://svn.plone.org/svn/collective/collective.transform.docbook',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.transform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'html2docbook'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
