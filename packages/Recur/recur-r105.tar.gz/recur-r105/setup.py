from setuptools import setup, find_packages
import sys, os

version = 'r105'

setup(name='recur',
      version=version,
      description="Iterators for datetime objects.",
      long_description="""
      The recur module provides iterators for datetime objects. Recurrence patterns can be provided in natural language strings like "every 3 days" or "Sept 14" (currently, only a English Locale is provided). For example, this code:
      d = recur.Recurrence(datetime.date(1999, 11, 28), "-5 each month")
      Will make "d" an iterator, producing datetime.date objects starting with datetime.date(1999, 12, 26), and then proceeding to the fifth-from-last date of each succeeding month.
      The recur module now includes a Worker class, which spawns new threads as needed to accomplish recurring tasks. Subclass it and override its "work" method. You can set its "paused" and "terminated" attributes to True/False as needed to manage a recurring task.
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Robert Brewer',
      author_email='',
      url='',
      license='',
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
      
