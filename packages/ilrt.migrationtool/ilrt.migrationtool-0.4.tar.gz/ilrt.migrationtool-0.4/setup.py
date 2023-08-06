from setuptools import setup, find_packages
import os

version = '0.4'

setup(name='ilrt.migrationtool',
      version=version,
      description="A site migration tool for Plone that uses the site's theme egg version releases",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
                       open(os.path.join("docs", "TODO.txt")).read(),      
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta"
        ],
      keywords='web zope plone migration setup release management workflow',
      author='Internet Development, ILRT, University of Bristol',
      author_email='internet-development@bris.ac.uk',
      url='https://svn.ilrt.bris.ac.uk/repos/pypi/ilrt.migrationtool',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ilrt'],
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
