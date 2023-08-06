from setuptools import setup, find_packages
import os

version = '0.2'

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''
    
    

setup(name='pydataportability.xrds',
      version=version,
      description="An XRDS parser",
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='dataportability xrds simple parser',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://mrtopf.de/blog',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pydataportability'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'elementtree',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
