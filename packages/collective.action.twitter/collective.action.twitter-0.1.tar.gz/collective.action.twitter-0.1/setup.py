from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.action.twitter',
      version=version,
      description="A contentrule action to publish something on twitter.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Hanno Schulz',
      author_email='hanno.schulz@catworkx.de',
      url='http://www.catworkx.de',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.action'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
        [z3c.autoinclude.plugin]
        target = plone
     # -*- Entry points: -*-
      """,
      )
