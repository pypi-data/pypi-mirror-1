from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('collective', 'collection', 'alphabetic', 'version.txt')[:-1]

long_description = (
                        open("README.txt").read() + "\n" +
                        open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
                        open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +
                        open(os.path.join("docs", "CREDITS.txt")).read()
    )

setup(name='collective.collection.alphabetic',
      version=version,
      description="Add alphabetic view for collection.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Taito Horiuchi',
      author_email='taito.horiuchi@abita.fi',
      url='http://pypi.python.org/pypi/collective.collection.alphabetic/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.collection'],
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
