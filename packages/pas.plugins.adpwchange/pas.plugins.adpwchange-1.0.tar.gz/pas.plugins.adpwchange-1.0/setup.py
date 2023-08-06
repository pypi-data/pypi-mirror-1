from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='pas.plugins.adpwchange',
      version=version,
      description="(Plone)PAS plugin to enable password changes in AD",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='AD PAS PlonePAS Plone',
      author='Wichert Akkerman',
      author_email='wichert@wiggy.net',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pas', 'pas.plugins'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "setuptools",
          "Products.PluggableAuthService",
          "Products.PlonePAS",
          "python-ad",
# Dependencies for python-ad, which does not declare them itself. 
# See http://code.google.com/p/python-ad/issues/detail?id=2
          "python-ldap",
          "dnspython",
          "PLY",
      ],
      entry_points="""
      """,
      )
