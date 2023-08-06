from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='collective.contentgenerator',
      version=version,
      description="Generates populated plone sites from specifed content profiles",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta"
        ],
      keywords='web zope plone test content generation profile',
      author='Plone Collective',
      author_email='internet-development@bristol.ac.uk',
      url='http://svn.plone.org/svn/collective/collective.contentgenerator',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
