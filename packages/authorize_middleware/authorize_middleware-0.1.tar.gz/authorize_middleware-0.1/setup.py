from setuptools import setup

PACKAGE = 'authorize_middleware'
VERSION = '0.1'

setup(name=PACKAGE,
        version=VERSION,
        description='An authorization middleware for WSGI applications',
        license = 'MIT',
        author='Dalius Dobravolskas',
        author_email='dalius@sandbox.lt',
        url='http://hg.sandbox.lt/authorize-middleware',
        packages=['authorize_middleware'],
        test_suite = 'nose.collector',
        include_package_data=True,
        install_requires = [
            "Paste>=1.4", "decorator>=2.1.0",
        ],
        extras_require = {
            'pylons': ["Pylons>=0.9.5,<=1.0"],
        },
)
