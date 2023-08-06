from setuptools import setup, find_packages

version = '0.1'

setup(name='pydataportability.xrds',
      version=version,
      description="An XRDS parser and generator",
      long_description="""\
handles XRDS files as described in http://xrds-simple.net/core/1.0/""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='dataportability xrds simple parser',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://mrtopf.de/blog',
      license='LGPL',
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
