from setuptools import setup, find_packages
import os.path

version = '0.1'

setup(name='plonerelations.ATField',
      version=version,
      description="ATField for plone.relations",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("plonerelations", "ATField", "ploneRelationsATField.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone.relation field widget archetypes',
      author='Alec Mitchell, Mika Tasich',
      author_email='apm13@columbia.edu',
      url='http://svn.plone.org/svn/collective/plonerelations.ATField',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonerelations'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.relations',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
