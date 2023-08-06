from setuptools import setup, find_packages
import os.path

versionfile = open(os.path.join('xm', 'portlets', 'version.txt'))
version = versionfile.read().strip()
versionfile.close()


setup(name='xm.portlets',
      version=version,
      description="Portlets for XM",
      long_description="""This module provide the portlet used in Plone with
      eXtremeManagement""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='xm portlets',
      author='Jean-Paul Ladage',
      author_email='j.ladage@zestsoftware.nl',
      url='http://svn.plone.org/svn/collective/xm.portlets',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xm'],
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
