from setuptools import setup

setup(
    name = 'VerConChk',
    version = '1.0',
    author = 'Daniel D. Beck',
    author_email = 'me@danieldbeck.com',
    packages = ['verconchk', 'verconchk.tests'],
    scripts = ['bin/vcc'],
    url = 'http://bitbucket.org/ddbeck/verconchk/',
    license = 'LICENSE.txt',
    description = ('a tool for finding and checking the status of version'
                   ' controlled files'),
    long_description = open('README.txt').read(),
)
