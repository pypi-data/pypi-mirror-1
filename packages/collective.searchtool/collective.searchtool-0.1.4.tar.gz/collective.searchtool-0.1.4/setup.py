from setuptools import setup, find_packages
import os

version = '0.1.4'

setup(name='collective.searchtool',
      version=version,
      description="Search tool for plone using z3c.form.",
      long_description = open(os.path.join('src', 'collective', 'searchtool', 'README.txt')).read() + '\n\n' +
                         open(os.path.join('src', 'collective', 'searchtool', 'HISTORY.txt')).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope plone search',
      author='Rok Garbas',
      author_email='rok@garbas.si',
      url='https://svn.plone.org/svn/collective/collective.searchtool',
      license='GPL',
      packages = find_packages('src', exclude=['ez_setup']),
      package_dir = {'':'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.z3cform',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
