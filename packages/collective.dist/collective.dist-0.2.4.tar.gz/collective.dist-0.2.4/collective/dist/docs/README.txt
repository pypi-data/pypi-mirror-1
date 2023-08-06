=======================
collective.dist package
=======================

.. contents::

What is collective.dist ?
=========================

I have added in Python 2.6 a new feature to allow people
to deal with several PyPI-like servers in `.pypirc`.

Basically you can use `register` and `upload` commands on any server
registered in `.pypirc`, which changed a bit.

But Plone and Zope runs on Python 2.4.

So this package adds two new commands so you can use what will be 
available in Python 2.6:

- **mupload**: command that allows uploading the package to several servers
- **mregister**: command that allow registering to several servers

This package also provides some new commands that will be introduced 
in Python 2.7:

- **check**: command that allows you to check if the metadata are compliant.
  It checks for example that long_description compiles in reSt.
  Notice that **mregister** calls this command.

How to use collective.dist ?
============================

**mregister** and **mupload** are replacing `register` and `upload` commands
and work with an extended version of the `.pypirc` file.

In order to work with it, change your `.pypirc` file this way::

    [distutils]
    index-servers = 
        pypi

    [pypi]
    username:user 
    password:password

Where `user` and `password` are your `PyPI` users.

With the latest changes, if *password* is omitted the user will be prompt 
to type it when needed.
 
You can then start to use the `mregister` and `mupload` commands, instead 
of the usual `register` and `upload` calls.

A typical call to upload your file would be::

    $ python setup.py mregister sdist mupload

To deal with several PyPI-like servers, you can add them in your
`.pypirc` file. 

For example, if you want to be able to push your packages to : 

- PyPI
- plone.org
- your own private PyPI (by using PloneSoftwareCenter for example)

You can write your `.pypirc` file like this::

    [distutils]
    index-servers = 
        pypi
        plone.org
        mycompany


    [pypi]
    username:user 
    password:password

    [plone.org]
    repository:http://plone.org/products
    username:ploneuser
    password:password

    [plone.org]
    repository:http://my.company/products
    username:user
    password:password

From there, you will be able to work with the different servers, 
with the `-r` option::
    
    $ python setup.py mregister sdist mupload -r http://plone.org

You can even use the section name instead of the url::

    $ python setup.py mregister sdist mupload -r plone.org

**If your package uses setuptools**, you can even create aliases to simplify
the command::

    $ python setup.py alias plone_release mregister sdist mupload -r plone.org  # creates the alias
    $ python setup.py plone_release # run the whole sequence

Another usage is to deal with several profiles on PyPI itself::

    [distutils]
    index-servers = 
        pypi
        pypi-personal

    [pypi]
    username:user 
    password:password

    [pypi-personal]
    username:user2 
    password:password2

Making sure your package metadata are fine
==========================================

You can check if your metadata are compliant by running the `check` command::

    $ python setup.py check

If you have docutils installed, you can even check if your `long_description` 
compiles, with the restructuredtext option::

    $ python setup.py check --restructuredtext

And make it raise an error in case of a problem with the strict option::

    $ python setup.py check --restructuredtext --strict

Notice that `mregister` calls `check` and check for reStructuredText.
If you want to make it stop when the reStructuredText is broken, use `strict`
as well::

    $ python setup.py mregister --strict

