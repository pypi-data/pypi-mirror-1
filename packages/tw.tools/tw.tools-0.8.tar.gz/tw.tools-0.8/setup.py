from setuptools import setup, find_packages
import sys, os

version = '0.8'

setup(name='tw.tools',
      version=version,
      description="Tools to aid toscawidget framework interactions.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='toscawidgets widgets turbogears',
      author='Christopher Perkins',
      author_email='chris@percious.com',
      url='http://toscawidgets.org/',
      download_url='http://toscawidgets.org/download',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
