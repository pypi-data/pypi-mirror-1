from setuptools import setup, find_packages
import os.path

version = '1.1'

setup(name='Products.PloneLDAP',
      version=version,
      description="LDAP/Active Directory support for Plone",
      long_description=open('README.txt').read() +
                      open(os.path.join('docs', 'CHANGES.txt')).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
        "License :: OSI Approved :: Zope Public License",
      ],
      keywords='Zope CMF Plone LDAP authentication',
      author='Wichert Akkerman - Simpon',
      author_email='wichert@simplon.biz',
      url='http://svn.plone.org/svn/collective/PloneLDAP',
      license='Zope Public License 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'Products.LDAPMultiPlugins',
        'Products.LDAPUserFolder',
      ],
)

