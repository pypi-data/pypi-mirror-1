A brief documentation
=====================

This recipe takes a number of options:

erlang-path
    The path where to find the erlc command (default = /usr/local/bin).

url
    The URL to download the ejabberd source distribution.

prefix
    Prefix path (default = <buildout directory>).
 

Tests
=====

We will define a buildout template used by the recipe:

    >>> buildout_cfg = """
    ... [buildout]
    ... parts = ejabberd
    ... offline = true
    ...
    ... [ejabberd]
    ... recipe = rod.recipe.ejabberd
    ... url = http://www.process-one.net/downloads/ejabberd/2.1.0-rc1/sources/ejabberd-2.1.0_rc1.tar.gz
    ... """

We'll start by creating a buildout:

    >>> import os.path
    >>> write('buildout.cfg', buildout_cfg)

Running the buildout gives us:

    >>> output = system(buildout)
    >>> if output.endswith("ejabberd\n"): True
    ... else: print output
    True
