from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='Products.MemoryProfiler',
      version=version,
      description="A memory profiler for zope",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Memory Profiler Zope',
      author='Youenn Boussard [ingeniweb]',
      author_email='y.boussard@ingeniweb.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'guppy',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
