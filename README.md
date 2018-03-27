Python Library for Golos
========================

This is a forked version of [piston-lib](https://github.com/xeroc/piston-lib) which is unmaintained.

This library uses websockets to communicate with golosd. The key difference from [golos-python](https://github.com/GolosChain/golos-python) is that piston-lib uses websockets while golos-python uses http API.

Installation
------------

Install with `pip3`:

    $ sudo apt-get install libffi-dev libssl-dev python-dev python3-pip
    $ pip3 install golos-piston

Manual installation:

    $ git clone https://github.com/bitfag/golos-piston.git
    $ cd golos-piston
    $ python3 setup.py install --user

Upgrade
-------

    $ pip3 install golos-piston --user --upgrade


Documentation
-------------

As golos-piston is a fork of piston-lib, you can use their documentation.

Thanks to readthedocs.io, the documentation can be viewed on
[lib.piston.rocks](http://lib.piston.rocks)

Documentation is written with the help of sphinx and can be compile to
html with:

    cd docs
    make html
