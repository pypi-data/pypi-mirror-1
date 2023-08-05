from setuptools import setup, find_packages

setup(
    name = "zc.creditcard",
    version = "1.0",
    author = "Zope Corporation",
    author_email = "zope3-dev#zope.org",
    description = "Utilities for credit card processing",
    keywords = "cc credit card",

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
       'zope.testing',
       'setuptools',
       ],
    dependency_links = ['http://download.zope.org/distribution/'],
    license = "ZPL 2.1",
    )
