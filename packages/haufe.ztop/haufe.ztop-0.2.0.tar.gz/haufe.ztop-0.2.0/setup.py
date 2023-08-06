from setuptools import setup, find_packages
import os

version = '0.2.0'

setup(name='haufe.ztop',
      version=version,
      description="Real-time Zope request analysis based on haufe.requestmonitoring",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Logging",
        ],
      keywords='',
      author='Haufe Mediengruppe',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      url='',
      license='ZPL (see LICENSE.txt)',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['haufe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points=dict(console_scripts=['ztop=haufe.ztop.ztop:main', 
                                         'zanalyze=haufe.ztop.zanalzye:main'],
          )
      )
