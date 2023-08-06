from setuptools import setup, find_packages
import os

version = '0.4'

setup(name='pydataportability.discovery',
      version=version,
      description="Christian Scholz",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='pydataportability dataportability acct xrd discovery webfinger finger google',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://pydataportability.org',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pydataportability'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'repoze.zcml',
          'repoze.component',
          'zope.configuration',
          'zope.interface',
          'pydataportability.xrd',
          'pydataportability.model.resource'
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'console_scripts': [
            'discover = pydataportability.discovery.discovery:main',
            'webfinger = pydataportability.discovery.discovery:webfinger',
            
        ],
        },
      )
