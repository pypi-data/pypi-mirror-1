from setuptools import setup, find_packages
import os

version = '1.0rc4'

setup(name='collective.xdv',
      version=version,
      description="Integrates the xdv Deliverance implementation with Plone using a post-publication hook to transform content",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone xdv deliverance theme transform xslt',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.xdv',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.synchronize',
          'plone.app.registry>=1.0a2',
          'dv.xdvserver',
      ],
      extras_require={
          'Zope2.10': ['ZPublisherEventsBackport'],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
