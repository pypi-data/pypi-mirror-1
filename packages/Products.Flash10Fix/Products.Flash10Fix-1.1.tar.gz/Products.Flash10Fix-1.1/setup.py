from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='Products.Flash10Fix',
      version=version,
      description="This package fixes http://dev.plone.org/plone/ticket/8624 which prevents .swf movies from playing in Flash 10 when served from Plone.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone",
        ],
      keywords='plone flash video swf',
      author='David Glick',
      author_email='davidglick@onenw.org',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
