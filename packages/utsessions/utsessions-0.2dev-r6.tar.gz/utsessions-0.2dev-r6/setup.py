from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='utsessions',
      version=version,
      description="Managing unique and timed sessions in Django",
      long_description=open("README.txt").read() + "\n",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='django python session unique user',
      author='Julien Fache',
      author_email='fantomas42@gmail.com',
      url='http://code.google.com/p/django-ut-sessions/',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      )
