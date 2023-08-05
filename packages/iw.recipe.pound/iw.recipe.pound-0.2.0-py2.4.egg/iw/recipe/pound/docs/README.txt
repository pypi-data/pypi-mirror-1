=======================
iw.recipe.pound package
=======================

.. contents::

What is iw.recipe.pound ?
=========================

`iw.recipe.pound` is a buildout recipe to compile and configure Pound.
It uses `zc.recipe.cmmi` then configure pound.cfg.

How to use iw.recipe.pound ?
============================

As a recipe, you have to provide a part in your buildout file::

    >>> from zc.buildout.testing import *
    >>> import getpass
    >>> owner = group = getpass.getuser()
    >>> import os; join = os.path.join 
    >>> data_dir = join(test_dir, 'data')
    >>> parts_dir = join(data_dir, 'parts')
    >>> bin_dir = join(data_dir, 'bin')
    >>> buildout = {'instance': {'location': test_dir},
    ...             'buildout': {'directory': test_dir,
    ...                          'parts-directory': parts_dir,
    ...                          'bin-directory': bin_dir}}
    >>> name = 'pound'
    >>> options = {'url': 'mypackage.tgz',
    ...            'owner': owner,
    ...            'group': owner}

For each balancer you want to create, you have to define it::

    >>> balancers = """\
    ...     one  80 127.0.0.1:8080 127.0.0.1:8081
    ...     two  90 127.0.0.1:8082 127.0.0.1:8083 169.1.1.2:80
    ... """
    >>> options['balancers'] = balancers

Each line is composed of the name and the port, and a list of
backends, defines by a host and a port.

Creating the recipe::

    >>> from iw.recipe.pound import Recipe
    >>> recipe = Recipe(buildout, name, options)

Running it::

    >>> paths = recipe.install()

Checking the files created::

    >>> paths
    ('...parts/pound', '...pound.cfg', '...pound')

    >>> location = paths[0]
    >>> os.listdir(join(location, 'sbin'))
    ['pound', 'poundctl']

Checking the pound.cfg created::

    >>> cfg = join(location, 'etc', 'pound.cfg')
    >>> print open(cfg).read()
    ## pound.cfg
    ## created by iw.recipe.pound
    <BLANKLINE>
    ## global options:
    User                "tziade"
    Group               "tziade"
    <BLANKLINE>
    ## Logging: (goes to syslog by default)
    ##  0       no logging
    ##  1       normal
    ##  2       extended
    ##  3       Apache-style (common log format)
    LogLevel    1
    <BLANKLINE>
    ## Log facility -- the manpage for syslog.conf(5) lists valid values.
    #LogFacility        daemon
    <BLANKLINE>
    ## check backend every X secs:
    Alive               30
    <BLANKLINE>
    ## use hardware-accelleration card supported by openssl(1):
    #SSLEngine  "<hw>"
    <BLANKLINE>
    ## listen, redirect and ... to:
    # balancer for one
    ListenHTTP
        Address 127.0.0.1
        Port    80
        # for webdav
        xHTTP   2
        Service
            BackEnd
                Address 127.0.0.1
                Port    8080
            End
            BackEnd
                Address 127.0.0.1
                Port    8081
            End
    <BLANKLINE>
        # for session cookies
        Session
                Type COOKIE
                ID "__ac"
                TTL 300
        End
        End
    End
    <BLANKLINE>
    # balancer for two
    ListenHTTP
        Address 127.0.0.1
        Port    90
        # for webdav
        xHTTP   2
        Service
            BackEnd
                Address 127.0.0.1
                Port    8082
            End
            BackEnd
                Address 127.0.0.1
                Port    8083
            End
            BackEnd
                Address 169.1.1.2
                Port    80
            End
    <BLANKLINE>
        # for session cookies
        Session
                Type COOKIE
                ID "__ac"
                TTL 300
        End
        End
    End
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>

We also have a general script that is added in the buildout binary folder::

    >>> print open(join(bin_dir, 'pound')).read()
    #!/bin/sh
    <BLANKLINE>
    /.../pound -f /.../pound.cfg -p /...pound.pid 
    <BLANKLINE>
    <BLANKLINE>

Cleaning up the files::

    >>> import shutil
    >>> shutil.rmtree(paths[0])

