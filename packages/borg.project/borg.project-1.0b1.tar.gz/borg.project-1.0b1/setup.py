from setuptools import setup, find_packages
import sys, os

version = '1.0b1'

setup(name='borg.project',
      version=version,
      description="Ability to create project workspaces with local workflow",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone project workspace teamspace',
      author='Martin Aspeli',
      author_email='optilude@gmx.net',
      url='http://svn.plone.org/svn/collective/borg/borg.project',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['borg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "borg.localrole",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
