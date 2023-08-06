from setuptools import setup, find_packages

setup(
    name='ldappas',
    version='0.7',
    author='Zope 3 developers',
    author_email='zope3-dev@zope.org',
    url='http://svn.zope.org/ldappas',
    description="""\
LDAP-based authenticator for Zope 3. It uses ldapadapter to talk to an
LDAP server.
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL 2.1',
    keywords='Zope3 authentication ldap',
    classifiers = ['Framework :: Zope 3'],
    install_requires=[
        'ZODB3',
        'ldapadapter>0.6',
        'setuptools',
        'zope.annotation',
        'zope.app.authentication',
        'zope.app.component',
        'zope.app.container',
        'zope.app.onlinehelp',
        'zope.app.zapi',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
    ],
    )
