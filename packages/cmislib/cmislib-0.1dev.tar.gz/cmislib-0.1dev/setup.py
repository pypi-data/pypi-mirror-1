from setuptools import setup, find_packages

version = '0.1'

setup(
    name = "cmislib",
    description = 'CMIS client library for Python',
    version = version,
    author = 'Jeff Potts',
    author_email = 'jeffpotts01@gmail.com',
    license = 'New BSD',
    url = 'http://code.google.com/p/cmislib/',
    package_dir = {'':'src'},
    packages = find_packages("src"),
    include_package_data = True,
)
