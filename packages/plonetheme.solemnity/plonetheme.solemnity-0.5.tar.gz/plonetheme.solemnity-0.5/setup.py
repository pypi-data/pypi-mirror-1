from setuptools import setup, find_packages
import os

version_file = os.path.join('plonetheme', 'solemnity', 'version.txt')
version = open(version_file).read().strip()

setup(name='plonetheme.solemnity',
      version=version,
      description="An installable theme for Plone 3.0 based on the solemnity theme by Six Shooter Media.",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme',
      author='Timo Stollenwerk',
      author_email='timo@zmag.de',
      url='http://svn.plone.org/svn/collective/plonetheme.solemnity',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonetheme'],
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
