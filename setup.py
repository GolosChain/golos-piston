#!/usr/bin/env python

import codecs

from setuptools import setup
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    codecs.register(lambda name, enc=ascii: {True: enc}.get(name == 'mbcs'))

VERSION = '0.6.0'

setup(
    name='golos-piston',
    version=VERSION,
    description='Python library for Golos',
    long_description=open('README.md').read(),
    download_url='https://github.com/bitfag/golos-piston/tarball/' + VERSION,
    author='Fabian Schuh',
    author_email='Fabian@chainsquad.com',
    maintainer='Vladimir Kamarzin',
    maintainer_email='vvk@vvk.pp.ru',
    url='http://lib.piston.rocks',
    keywords=['golos', 'steem', 'library', 'api', 'rpc', 'transactions'],
    packages=["piston", "pistonapi", "pistonbase"],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial',
    ],
    install_requires=[
        "graphenelib>=0.5.3",
        "websockets>=2.0",
        "scrypt>=0.7.1",
        "diff-match-patch>=20121119",
        "appdirs>=1.4.0",
        "python-frontmatter>=0.2.1",
        "funcy",
        "python-dateutil>=2.6.1",
        "pycryptodome"
        # "python-dateutil",
        # "secp256k1==0.13.2"
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
)
