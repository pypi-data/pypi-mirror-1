from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.soupstrainer',
      version=version,
      description="Clean up HTML using BeautifulSoup and filter rules.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='',
      author='Florian Schulze',
      author_email='florian.schulze@gmx.net',
      url='http://svn.plone.org/svn/collective/collective.soupstrainer',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'BeautifulSoup',
      ],
      entry_points={
        'console_scripts': ['soupstrainer = collective.soupstrainer:main'],
      },
      test_suite = "collective.soupstrainer",
      )
