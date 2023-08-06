from setuptools import setup, find_packages
import os

version = '0.6.2'

setup(name='Products.CMFQuestionnaire',
      version=version,
      description="A simple questionnaire for Plone.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone, questionnaire',
      author='H. Turgut Uyar',
      author_email='uyar@tekir.org',
      url='http://plone.org/products/cmfquestionnaire',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
