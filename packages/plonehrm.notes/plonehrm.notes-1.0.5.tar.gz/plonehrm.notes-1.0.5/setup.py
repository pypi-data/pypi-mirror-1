from setuptools import setup, find_packages
import os.path


def get_file_contents_from_main_dir(filename):
    file_path = os.path.join('plonehrm', 'notes', filename)
    this_file = open(file_path)
    contents = this_file.read().strip()
    this_file.close()
    return contents

version = get_file_contents_from_main_dir('version.txt')
history = get_file_contents_from_main_dir('HISTORY.txt')
readme = get_file_contents_from_main_dir('README.txt')
long = "%s\n\n\n%s" % (readme, history)

setup(name='plonehrm.notes',
      version=version,
      description="A plonehrm extension module to add notes to an employee.",
      long_description=long,
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
          'collective.autopermission',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
