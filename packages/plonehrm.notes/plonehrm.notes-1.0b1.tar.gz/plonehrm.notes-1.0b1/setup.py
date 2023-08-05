from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='plonehrm.notes',
      version=version,
      description="A plonehrm extension module to add note to an employee.",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='hrm notes',
      author='Jean-Paul Ladage',
      author_email='j.ladage@zestsoftware.nl',
      url='http://svn.plone.org/svn/collective/plonehrm.notes',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonehrm'],
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
