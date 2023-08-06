from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='teamrubber.googlechart',
      version=version,
      description="Provides a Zope object that acts as a wrapper for pygooglechart",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Framework :: Zope2",
        "Framework :: Plone",
        
        ],
      keywords='zope plone googlechart',
      author='Richard Wilson',
      author_email='team@teamrubber.com',
      url='http://www.teamrubber.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['teamrubber'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pygooglechart'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
