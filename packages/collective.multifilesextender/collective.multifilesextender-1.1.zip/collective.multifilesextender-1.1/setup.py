from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='collective.multifilesextender',
      version=version,
      description="This package extends any AT content type by a multi file field",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='multifile, schemaextender, attachments',
      author='Matous Hora',
      author_email='matous.hora@dms4u.cz',
      url='http://pypi.python.org/pypi/collective.multifilesextender',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'archetypes.schemaextender',
          'archetypes.multifile',
      ],
      entry_points="""
      """,
      paster_plugins = ["ZopeSkel"],
      )
