from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "pipbox", "version.txt")).read()

setup(name='Products.pipbox',
      version=version,
      description="Picture In Picture (lightbox/greybox) support for Plone",
      long_description=open(os.path.join("Products", "pipbox", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "pipbox", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme',
      author='Steve McMahon',
      author_email='steve@dcn.org',
      url='http://svn.plone.org/svn/collective/Products.pipbox',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.jquerytools>=1.0b5',
      ],
      entry_points="""
          [z3c.autoinclude.plugin]
          target = plone
      """,
      )
