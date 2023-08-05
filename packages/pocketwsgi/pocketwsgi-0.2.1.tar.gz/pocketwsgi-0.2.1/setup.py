from setuptools import setup, find_packages
try:
    import buildutils
except ImportError:
    pass
import sys, os

version = '0.2.1'

setup(name='pocketwsgi',
      version=version,
      description="tiny wsgi application framework",
      long_description="""\
""",
      classifiers=[
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='wsgi',
      author='Atsushi Odagiri',
      author_email='aodagx@gmail.com',
      url='http://aodagx.ddo.jp/aodag/projects/pocketwsgi',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        # -*- Extra requirements: -*-
        'Tempita',
        'WebOb',
        'selector',
        'FormEncode',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
