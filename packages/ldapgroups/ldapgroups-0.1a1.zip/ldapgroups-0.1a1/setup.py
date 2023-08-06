from setuptools import setup, find_packages

setup(
    name='ldapgroups',
    version='0.1a1',
    author='Jeroen Michiel',
    author_email='jmichiel@yahoo.com',
    url='http://code.google.com/p/ldapgroups',
    description="""\
A read-only Zope3 GroupFolder implementation that reflects groups on an LDAP server.
Needs ldappas
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='MIT',
    keywords='Zope3 ldap group folder',
    classifiers = ['Framework :: Zope3',
                   'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP'],
    install_requires=['ldappas>=0.7']
    )
