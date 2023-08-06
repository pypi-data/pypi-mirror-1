from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='ely.portlets.image',
      version=version,
      description="A portlet for attaching and linking a single image",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone portlet image',
      author='Matt Halstead',
      author_email='matt@elyt.com',
      url='http://code.google.com/p/ely/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ely', 'ely.portlets'],
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
