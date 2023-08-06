from setuptools import setup

PACKAGE = 'authopenid_middleware'
VERSION = '0.2.1'

setup(name=PACKAGE,
        version=VERSION,
        description='OpenID authentication middleware for WSGI applications',
        license = 'MIT',
        author='Dalius Dobravolskas',
        author_email='dalius@sandbox.lt',
        url='http://trac.sandbox.lt/auth/wiki/AuthOpenIdMiddleware',
        packages=['authopenid_middleware'],
        test_suite = 'nose.collector',
        include_package_data=True,
        install_requires = [
            "distribute", "Paste>=1.4", "decorator>=2.1.0", "python-openid>=2.1.0", "Beaker>=0.7.3"
        ],
        extras_require = {
            'pylons': ["Pylons>=0.9.5,<=1.0"],
        },
)
