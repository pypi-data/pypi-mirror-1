from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='hexagonit.form',
      version=version,
      description="Orderable variant of zope.formlib.form.Fields.",
      long_description="""\
Drop-in replacement for the ``zope.formlib.form.Fields`` class that
implements support for ordering form fields in the same manner that
the Archetypes Schema class does.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Zope Public License",
        ],
      keywords='formlib fields ordering',
      author='Kai Lautaportti',
      author_email='kai.lautaportti@hexagonit.fi',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['hexagonit'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
