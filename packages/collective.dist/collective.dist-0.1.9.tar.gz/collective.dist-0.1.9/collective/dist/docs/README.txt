=======================
collective.dist package
=======================

.. contents::

What is collective.dist ?
=========================

This package adds two new commands to distutils:

- **mupload**: command that allows uploading the package to several servers
- **mregister**: command that allow registering to several servers

How to use collective.dist ?
============================

**mregister** and **mupload** are replacing `register` and `upload` command
and work with an extended version of the `.pypirc` file.

In order to work with it, change your .pypirc file this way::

    [distutils]
    index-servers = 
        pypi

    [pypi]
    username:user 
    password:password

Where `user` and `password` are your `PyPI` users.

You can then start to use the commands, instead of the usual `register`
and `upload` calls.

A typical call to upload your file would be::

    $ python setup.py mregister sdist bdist_egg mupload

To deal with several PyPI-like servers, you can add them in your
`.pypirc` file::

    [distutils]
    index-servers = 
        pypi
        another

    [pypi]
    username:user 
    password:password

    [another]
    repository:http://another.pypi.server    
    username:user2 
    password:password2
    
Then work with it, with the `-r` option::
    
    $ python setup.py mregister sdist bdist_egg mupload -r http://another.pypi.server

You can even use the section name instead of the url::

    $ python setup.py mregister sdist bdist_egg mupload -r another

And use an alias to make the code simpler::

    $ python setup.py alias to_another mregister sdist bdist_egg mupload -r another  # creates the alias
    $ python setup.py to_another # run the whole sequence

