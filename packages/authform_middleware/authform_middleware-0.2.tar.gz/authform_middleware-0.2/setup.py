from setuptools import setup

PACKAGE = 'authform_middleware'
VERSION = '0.2'

setup(name=PACKAGE,
        version=VERSION,
        description='Form authentication middleware for WSGI applications',
        license = 'MIT',
        author='Dalius Dobravolskas',
        author_email='dalius@sandbox.lt',
        url='http://hg.sandbox.lt/authform-middleware',
        packages=['authform_middleware'],
        test_suite = 'nose.collector',
        include_package_data=True,
        install_requires = [
            "distribute", "Paste>=1.4", "Beaker>=0.7.3"
        ],
        extras_require = {
            'pylons': ["Pylons>=0.9.5,<=1.0"],
        },
)
