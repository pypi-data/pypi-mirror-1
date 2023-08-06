from setuptools import setup, find_packages
import os


def get_file_contents_from_main_dir(filename):
    file_path = os.path.join('Products', 'plonehrm', filename)
    this_file = open(file_path)
    contents = this_file.read().strip()
    this_file.close()
    return contents

version = get_file_contents_from_main_dir('version.txt')
history = get_file_contents_from_main_dir('HISTORY.txt')
readme = get_file_contents_from_main_dir('README.txt')
long = "%s\n\n\n%s" % (readme, history)

setup(name='Products.plonehrm',
      version=version,
      description="Human Resource Management in Plone",
      long_description=long,
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url="",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plonehrm.absence>=1.0b5',
          'plonehrm.checklist',
          'plonehrm.contracts>=2.0.4',
          'plonehrm.jobperformance',
          'plonehrm.notes',
          'plonehrm.notifications',
          'plonehrm.personaldata>=2.0',
          'collective.autopermission',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
