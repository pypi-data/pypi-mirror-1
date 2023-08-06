# -*- coding: iso-8859-15 -*-

try:
    from setuptools import setup, find_packages
except ImportError, e:
    from ez_setup import use_setuptools
    use_setuptools()
finally:
    from setuptools import setup, find_packages

setup(
    name = 'stellaris.client',
    version = '0.0.3',
    author='Mikael Hoegqvist',
    author_email='hoegqvist@zib.de',
    url='http://pypi.python.org/pypi/benri.client/',
    download_url='',
    description='A StellarIS client package.',
    license='Apache 2.0',
    long_description="""A StellarIS client package.""",    
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    
    install_requires = [
    'benri.client >= 0.0.1',
    "httplib2 >= 0.4.0",
    "simplejson >= 1.7.3"    
    ],
    scripts=['scripts/stellaris-client'],
    namespace_packages = ['stellaris'],
     classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries',
    ],    
    )
