from setuptools import setup, find_packages
import sys, os


execfile(os.path.join("emencia_django_admin", "release.py"))

version = __VERSION__

setup(
      name=__PROJECT__,
      version=__VERSION__,
      description=__DESCRIPTION__,
      author=__AUTHOR__,
      author_email=__EMAIL__,
      url=__URL__,
      license = __LICENSE__,
      copyright = __COPYRIGHT__,
      classifiers=["Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
