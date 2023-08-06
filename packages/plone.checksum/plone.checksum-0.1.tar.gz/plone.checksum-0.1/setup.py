from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version=read("plone", "checksum", "version.txt").strip()

long_description=(
        read("README.txt")
        + "\n" +
        read("plone", "checksum", "README.txt")
        + "\n" +
        read("plone", "checksum", "BlobFile.txt")
        + "\n" +
        read("plone", "checksum", "browser", "README.txt")
        + "\n" +
        read("plone", "checksum", "browser", "CMFEditions.txt")
        + "\n" +
        read("docs", "HISTORY.txt")
        )

setup(name='plone.checksum',
      version=version,
      description="Checksums for ZODB",
      long_description=long_description,
      classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zodb zope integrity',
      author='Jazkarta',
      author_email='team@jazkarta.com',
      url='http://svn.plone.org/svn/collective/plone.checksum',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'RuleDispatch',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      dependency_links=[
          'http://peak.telecommunity.com/snapshots/',
      ],

      )
