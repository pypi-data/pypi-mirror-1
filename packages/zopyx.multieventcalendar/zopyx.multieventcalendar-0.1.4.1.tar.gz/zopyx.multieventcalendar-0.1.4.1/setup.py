from setuptools import setup, find_packages
import os

version = '0.1.4.1'

setup(name='zopyx.multieventcalendar',
      version=version,
      description="A multi-event calendar for Plone 3.X",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Event Calendaring Plone',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://svn.plone.org/svn/collective/zopyx.multieventcalendar',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopyx'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
