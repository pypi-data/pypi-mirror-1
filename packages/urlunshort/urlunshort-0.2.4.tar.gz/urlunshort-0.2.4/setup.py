from setuptools import setup, find_packages
import sys, os

import urlunshort
author, email = urlunshort.__author__[:-1].split(' <')

setup(name='urlunshort',
      version=urlunshort.__version__,
      description=urlunshort.__doc__,
      long_description=open("README").read(),
      classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Topic :: Internet :: WWW/HTTP"
            ],
      keywords='',
      author=author,
      author_email=email,
      url=urlunshort.__homepage__,
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      entry_points={
        'console_scripts': [
            'urlunshort = urlunshort.console:entrypoint_urlunshort',
            ],
        },
      zip_safe=False,
      test_suite = 'nose.collector',
      )
