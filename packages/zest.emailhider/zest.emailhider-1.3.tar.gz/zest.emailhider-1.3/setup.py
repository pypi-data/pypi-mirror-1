from setuptools import setup, find_packages
import os

version = open(os.path.join('zest', 'emailhider', "version.txt")
               ).read().strip()

setup(name='zest.emailhider',
      version=version,
      description="A simple KSS component for hiding email addreses from spammers.",
      long_description=(
    open(os.path.join('zest', 'emailhider', "README.txt")).read()
    + "\n" +
    open(os.path.join("zest", "emailhider", "HISTORY.txt")).read()),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zestsoftware email spamprotection kss',
      author='Zest Software',
      author_email='s.hildebrandt@zestsoftware.nl',
      url='http://zestsoftware.nl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zest'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
	  'kss.plugin.cacheability',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
