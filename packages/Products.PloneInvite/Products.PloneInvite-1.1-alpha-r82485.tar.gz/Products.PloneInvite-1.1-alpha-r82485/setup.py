from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "PloneInvite", "version.txt")).read().strip()

setup(name='Products.PloneInvite',
      version=version,
      description="Allows users to invite others to join the site",
      long_description=open(os.path.join("Products", "PloneInvite", "README.txt")).read().decode('UTF8').encode('ASCII', 'replace'),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone"
        ],
      keywords='Plone PloneInvite',
      author='Kees Hink',
      author_email='hink@gw20e.com',
      url='http://www.gw20e.com',
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
