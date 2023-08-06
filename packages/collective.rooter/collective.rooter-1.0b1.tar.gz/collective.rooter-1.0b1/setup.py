from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='collective.rooter',
      version=version,
      description="Tools to force catalog queries to obey the current navigation root",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone navigation root',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.rooter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.monkeypatcher',
      ],
      entry_points="""
      """,
      )
