from setuptools import setup, find_packages

version = '0.1'

setup(name='pydataportability.microformats.base',
      version=version,
      description="Microformats Parser for Python",
      long_description="""\
this is an extensible Microformats parser for python""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='python microformats hcard hevent xfn rel dataportability',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://mrtopf.de/blog',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pydataportability.microformats','pydataportability'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zope.component',
          'elementtree',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
