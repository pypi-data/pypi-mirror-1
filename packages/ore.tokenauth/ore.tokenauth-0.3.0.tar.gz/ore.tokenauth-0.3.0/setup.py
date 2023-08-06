from setuptools import setup, find_packages

setup(
    name="ore.tokenauth",
    version="0.3.0",
    packages=find_packages('.', exclude=["*.tests"]),
    install_requires=['plone.keyring','setuptools', 'zope.app.authentication'],    
    namespace_packages=['ore'],
    url="http://svn.objectrealms.net/view/public/browser/ore.tokenauth/trunk",
    package_data = {
    '': ['*.txt', '*.zcml', '*.pt'],
    },
    zip_safe=True,
    author='Kapil Thangavelu',
    author_email='kapil.foss@gmail.com',
    description="""\
A secure session authentication scheme based on signed tokens. This is an accessory
to an underlying auth mechanism to provide for sessions. Its main purpose is to
avoid the need to pass credentials each request, in addition to avoiding the need
for passing credentials each request or utilizing a server side session.

This implementation is based off plone.session by wichert akkerman.
""",
    license='GPL',
    keywords="zope authentication",
    classifiers=['Programming Language :: Python',
                 'Environment :: Web Environment',
                 "License :: OSI Approved :: Zope Public License",                 
                 'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                 'Framework :: Zope3',
                 ],
    )
