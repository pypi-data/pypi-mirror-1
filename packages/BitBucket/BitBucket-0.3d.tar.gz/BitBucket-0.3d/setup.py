try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__version__ = '0.3d'

setup(name="BitBucket",
      version=__version__,
      description="Module for accessing Amazon S3",
      long_description="Provides a pythonic interface to Amazon's S3 Service.",
      keywords="web services amazon s3",
      author="Mitch Garnaat",
      author_email="mitch@garnaat.org",
      url="http://other10percent.com/?cat=9",
      packages=['s3amazon'],
      py_modules=['bitbucket'],
      scripts=['bb_example.py', 'bb_shell.py', 'test_filter.py'],
      data_files=['bitbucket_example.cfg'],
      )

