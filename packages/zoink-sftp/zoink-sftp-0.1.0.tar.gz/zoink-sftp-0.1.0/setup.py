"""
Project's setuptool configuration.

This should eggify and upload to pypi without problems.

Oisin Mulvihill
2009-02-04

"""
from setuptools import setup, find_packages

Name='zoink-sftp'
ProjecUrl="" #""
Version='0.1.0'
Author='Zeth and Oisin Mulvihill'
AuthorEmail='oisin dot mulvihill at gmail com'
Maintainer=' Oisin Mulvihill'
Summary='Friendly Python SSH2 interface allowing easy file and directory transfer.'
License='LGPL'
ShortDescription="Friendly Python SSH2 interface allowing easy file and directory transfer. This \
does not wrap the sftp command line tool"

# Recover the ReStructuredText docs:
fd = file("lib/zoinksftp/doc/zoink-sftp.stx")
Description=fd.read()
fd.close()

TestSuite = 'zoinksftp.tests'

needed = [
    'paramiko',
]


ProjectScripts = [
#    '',
]

PackageData = {
    # If any package contains *.txt or *.rst files, include them:
    '': ['*.txt', '*.rst', 'ini'],
}

setup(
#    url=ProjecUrl,
    name=Name,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    license=License,
    test_suite=TestSuite,
    scripts=ProjectScripts,
    install_requires=needed,
    packages=find_packages('lib'),
    package_data=PackageData,
    package_dir = {'': 'lib'},
)
