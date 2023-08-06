from setuptools import setup, find_packages
import os

version = '0.1b1'

setup(name='collective.z3cform.kss',
      version=version,
      description="enable inline validation with z3c form",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Jean-Francois Roche',
      author_email='jfroche@affinitic.be',
      url='http://svn.plone.org/svn/collective/collective.z3cform.kss/trunk/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'kss.core',
          'plone.z3cform',
          'plone.app.form',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
