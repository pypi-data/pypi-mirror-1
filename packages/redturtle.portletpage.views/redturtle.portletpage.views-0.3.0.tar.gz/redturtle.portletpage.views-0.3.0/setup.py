from setuptools import setup, find_packages
import os

version = '0.3.0'

setup(name='redturtle.portletpage.views',
      version=version,
      description="Additional views for Plone collective.portletpage product",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='portlet view portletpage',
      author='Massimo Azzolini',
      author_email='massimo@redturtle.net',
      url='https://code.redturtle.it/svn/redturtle/redturtle.net/redturtle.portletpage.views/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle', 'redturtle.portletpage'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.portletpage',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
