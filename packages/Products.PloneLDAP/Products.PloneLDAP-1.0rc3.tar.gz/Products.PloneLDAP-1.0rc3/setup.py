from setuptools import setup, find_packages

version = '1.0rc3'

setup(name='Products.PloneLDAP',
      version=version,
      description="LDAP/AD support for Plone",
      long_description=open('Products/PloneLDAP/README.txt').read() +
                      open('Products/PloneLDAP/CHANGES.txt').read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
      ],
      keywords='Zope CMF Plone LDAP authentication',
      author='Wichert Akkerman - Simpon',
      author_email='wichert@simplon.biz',
      url='http://svn.plone.org/svn/collective/PloneLDAP',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
)
