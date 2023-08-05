from setuptools import setup, find_packages

version = '1.0b1'

setup(name='simplon.plone.ldap',
      version=version,
      description="LDAP control panel for Plone 3",
      long_description=open("README.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
        ],
      keywords='plone ldap',
      author='Wichert Akkerman - Simplon',
      author_email='wichert@simplon.biz',
      url='http://code.simplon.biz/svn/zope/simplon.plone.ldap',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['simplon.plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
#          "python-ldap",
          "setuptools"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
