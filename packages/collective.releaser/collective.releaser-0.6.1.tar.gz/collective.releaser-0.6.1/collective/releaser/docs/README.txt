===========================
collective.releaser package
===========================

Report any bug or feature requests to : http://trac.ingeniweb.com

.. contents::

What is collective.releaser ?
=============================

collective.releaser provides command line utilities to make it easier to release
and deploy zc.buildout/subversion based projects.

It provides:

- new setuptools commands 

 - `release`: used to release an egg-based package
 - `build_mo`: used to search and compile .po file

- console scripts

 - `project_release`: used to release a buildout based project
 - `project_deploy`: used to deploy a buildout based project
 - `project_copy_eggs`: used to collect all eggs used in a project
 - `project_md5`: used to compute the MD5 hash of a buildout project
 - `package_svn_prepare`: to restructure a new created package to be svn ready

- a hook to be able to launch actions when a package is released, 
  with a default one that sends an email on each release.

- a paste template to create a project structure, called `releaser_project`.

How to install collective.releaser ?
====================================

To install `collective.releaser`, you just need to run easy_install::

    $ easy_install collective.releaser

or you can launch its setup if you have downloaded it::

    $ python setup.py install

How to use collective.releaser ?
================================

To work with collective.releaser, let's do a small tutorial on how to create
a buildbout-based project. This is done in a few steps:

- setting up your environment
- creating the project structure
- creating egg-based packages 
- releasing eggs
- releasing the buildout
- upgrading an existing buildout

Setting up your environement
::::::::::::::::::::::::::::

The first thing to do to work smoothly with zc.buildout is to set up a
few things on your environment that apply globally to any Buildout-based
applications.

Put two files in your home directory:

- `HOME/.buildout/.httpauth`: this file will contain the authentication
  information if the system tries to reach a http(s) ressource which is
  password protected (like a svn server or a private web site). 
  It is a text file where each line is: realm,url,user,password

  For example::

    trac,https://svn.ingeniweb.com,user,password
    pypi,http://products.ingeniweb.com,user,password

  This is used by `lovely.buildouthttp`.

- `HOME/.buildout/default.cfg`: This file set some defaults values, so 
  Buildout can cache and spare downloaded eggs. 
  
  For example::

    [buildout]
    download-cache = /home/tarek/.buildout/downloads
    eggs-directory = /home/tarek/.buildout/eggs

Next, you need to make sure you can release your eggs to several 
targets, because you may want some private eggs not to be published on
PyPI. At this time, the only software that provides the same
web services than PyPI is Plone Software Center >= 1.5.

To make it possible to handle several PyPI-like servers, 
we need to install a small add-on, called `collective.dist`::

    $ easy_install collective.dist

This will allow you to define several servers in your ~/.pypirc file.
For instance if you are working with a private PyPI-like server you can
define it like this in HOME/.pypirc ::

    [distutils]
    index-servers =
        pypi
        ingeniweb-public

    [pypi]
    username:ingeniweb
    password:secret

    [ingeniweb-public]
    repository:http://products.ingeniweb.com/catalog
    username:ingeniweb
    password:secret

Last, you need to define the release strategy configuration, that
will define for each target server the list of packages that must be released
there (regular expressions) and the command sequence that is used
with setup.py. Here's a default example, that can be added in your `.pypirc`
as well, by completing the sections with `release-command` and
`release-packages` variables::
    
    ...

    [ingeniweb-public]
    ...
    release-command = mregister sdist build_mo bdist_egg mupload
    release-packages =
        ^iw\..*

    [pypi]
    ...
    release-command = mregister sdist build_mo bdist_egg mupload
    release-packages =
        ^plone\..*
        ^collective\..*

This will push all eggs that starts with `plone.` or `collective.` 
to PyPI and all eggs that starts with `iw.` to ingeniweb-public.
The command used to push the packages are defined by `command`.

Creating the project structure
::::::::::::::::::::::::::::::

Every project must be structured the same way::
    
    $ paster create -t releaser_project my_project

This will ask you for a few values:

- project_name: the name of the project
- project_repo: the root of the subversion repository
- some more values that can be left to default.

This will generate a set of folders in `my_project`::

    $ ls my_project
    ./buildout
    ./bundles
    ./docs
    ./packages
    ./releases

Each folder has a role:

- buildout: contains the buildout configuration files
- bundles: contains the bundle used to work in develop mode
- docs: contains the documentation about the project
- packages: contains the egg-based package(s)
- releases: contains the releases of the buildout

This structure must be commited in subversion::
    
    $ svn import my_project http://some.svn/my_project -m "initial commit"

You will then be able to work in your buildout.

Creating egg-based package
::::::::::::::::::::::::::

From there you can add some packages into the project, by putting them
in the `packages` folder, by using any template available in ZopeSkel.

**Be carefull though, you must use a trunk/tags/branches structure in
packages for each project.**

::

    $ cd my_projet/packages    
    $ paster create -t plone plone.example
    $ package_svn_prepare plone.example

The last command just does the following::

    $ mv plone.example plone.example_md5_of_plone.example
    $ mkdir plone.example
    $ mkdir plone.example/tags plone.example/branches
    $ mv plone.example_md5_of_plone.example plone.example/trunk
    $ svn add plone.example
    $ svn ci -m "initial import of  plone.example"

**Do not use trunk as a package name with paster, as this will generate
bad metadata in the package.**

A special section can be added into `setup.cfg`, in order
to send a mail everytime the package is released::

    [mail_hook]
    hook = collective.releaser:mail
    from = support@ingeniweb.com
    emails =
         trac@lists.ingeniweb.com

If your system does not have a SMTP server, you will need to add 
the name of a SMTP server, and its port in your .pypirc file,
in a `mail_hook` section::

    [mail_hook]
    host = smtp.neuf.fr
    port = 25
    
From there you can bind the package to your buildout, with a develop 
variable, in your `my_project/buildout folder`::

    [buildout]
    ...
    develop=
        .../packages/monprojet.reports/trunk

The `bundle` folder can also be used to set svn:externals to make it
simpler to work in the buildout.

Releasing eggs 
::::::::::::::

Releasing eggs is done by calling `release` from a package::

    $ python setup.py release
    running release
    This package is version 0.1.2
    Do you want to run tests before releasing ? [y/N]: N
    Do you want to create the release ? If no, you will just be able to deploy again the current release [y/N]: Y
    Enter a version [0.1.2]: 0.1.2
    Commiting changes...
    Creating branches...
    ...

This will take care of:

- upgrading the setup.py version
- creating a branch and a tag in svn
- pushing the package to the various PyPI-like servers
- sending a mail with the changes, if the mail_hook section was provided in setup.cfg

Releasing the project 
:::::::::::::::::::::

Releasing the project consists of calling `project_release` then
`project_deploy`.

`project_release` will just create a new branch in subversion::

    $ cd my_project/buildout
    $ project_release
    What version you are releasing ? 0.1
    Added version file.

This will copy `my_project/buildout` to `my_project/releases/0.1` in 
subversion. You can then work in this release, to pinpoint the versions
in your buildout. A good practice is to create a dedicated cfg file
for deployment.

The next step is to generate a tarball with `project_deploy`::

    $ cd /tmp
    $ svn co http://somesvn/my_projet/releases/0.1 my_project
    $ cd my_project
    $ project_deploy prod.cfg

This will build a tarball in `/tmp` using VirtualEnv, and set everything up
so the buildout can be reinstalled offline anywhere with this archive.

The resulting release can be installed with two lines::

    $ python boostrap.py
    $ bin/buildout

Upgrading an existing buildout
::::::::::::::::::::::::::::::

To upgrade an existing buildout, you can use the `project_eggs` command.
It will create a tarball with all eggs needed to run the project and the 
.cfg file.

Run it in your buildout, by pointing the .cfg and by providing a name of
the archive::

    $ project_eggs buildout.cfg /tmp/upgrade.tgz

You can even give a filter to collect specific packages
with glob-like names, separated by commas::

    $ project_eggs buildout.cfg /tmp/upgrade.tgz "iw.*,plone.*"

This filter will only get the eggs starting with `iw.` and `plone.`.
This is useful when you have changed only a few eggs, and want to 
reduce the size of the tarball for the upgrade.

Doing an upgrade will then consist of calling::

    $ cp upgrade.tgz my_project/
    $ cd my_project
    $ tar -xzvf upgrade.tgz     
    $ bin/buildout

