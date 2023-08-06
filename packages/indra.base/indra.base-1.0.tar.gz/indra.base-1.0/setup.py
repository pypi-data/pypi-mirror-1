from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='indra.base',
      version=version,
      description="Second Life/OGP support library for handling uuid and llsd",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='lindenlab secondlife ogp llsd lluuid uuid indra',
      author='Linden Lab',
      author_email='info@lindenlab.com',
      url='http://wiki.secondlife.com/wiki',
      license='MIT License',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['indra'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'indra.util',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
