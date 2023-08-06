from setuptools import setup, find_packages
import os

version = '0.3.2'

setup(name='Products.ATMemberSelectWidgetNG',
      version=version,
      description="An archetypes widget similar to ATReferenceBrowserWidget which allows you to select a member's id or email from a popup search window. It can even be used without archetypes being installed in the site.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Junyong Pan',
      author_email='panjy@zopen.cn',
      url='http://plone.org/products/atmsw/',
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
