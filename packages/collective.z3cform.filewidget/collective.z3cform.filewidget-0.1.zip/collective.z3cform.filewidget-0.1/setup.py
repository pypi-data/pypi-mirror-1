from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.z3cform.filewidget',
      version=version,
      description="Simple editable filewidget for z3c forms",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='z3cform file widget plone',
      author='Matous Hora',
      author_email='matous.hora@dms4u.cz',
      url='http://pypi.python.org/pypi/collective.z3cform.filewidget',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
