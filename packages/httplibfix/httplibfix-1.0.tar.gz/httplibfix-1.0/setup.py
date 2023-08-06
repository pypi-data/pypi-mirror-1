from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='httplibfix',
      version=version,
      description="A fix to httplib in python2.4 to back port a patch from trunk to fix issues with rss reads.",
      long_description="""\
For details see Bug: http://bugs.python.org/issue900744

""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python http httplib rss patch',
      author='Matt Hamilton',
      author_email='matth@netsight.co.uk',
      url='http://pypi.python.org/pypi/httplibfix',
      license='GPL',
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
