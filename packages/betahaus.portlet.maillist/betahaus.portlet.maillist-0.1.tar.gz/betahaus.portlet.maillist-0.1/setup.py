from setuptools import setup, find_packages
import os

version = '0.1'
name = 'betahaus.portlet.maillist'

setup(name=name,
      version=version,
      description="Subscribe or unsubscribe from maillists",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Martin Lundwall',
      author_email='martin@betahaus.net',
      url='http://pypi.python.org/pypi/'+name,
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['betahaus', 'betahaus.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
