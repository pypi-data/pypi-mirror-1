from setuptools import setup, find_packages
import os

version = '0.1b'

setup(name='betahaus.livesearch',
      version=version,
      description="Replaces regular livesearch with a sane template",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        ],
      keywords='plone',
      author='Robin Harms Oredsson',
      author_email='robin@betahaus.net',
      url='http://pypi.python.org/pypi/betahaus.livesearch',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['betahaus'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
