from setuptools import setup

PACKAGE = 'openidprovider_middleware'
VERSION = '0.1'

setup(name=PACKAGE,
        version=VERSION,
        description='OpenID provider middleware for WSGI applications',
        license = 'MIT',
        author='Dalius Dobravolskas',
        author_email='dalius@sandbox.lt',
        url='http://hg.sandbox.lt/openidprovider-middleware',
        packages=['openidprovider_middleware'],
        test_suite = 'nose.collector',
        include_package_data=True,
        install_requires = [
            "Paste>=1.4", "python-openid>=2.1.0", "Beaker>=0.7.3"
        ],
)
