Plone Scholarly Journal
***********************

The ``Plone Scholarly Journal`` (PSJ) is a collection of packages to
create and maintain scholarly journals using Plone.

The special abilities of PSJ are:

 * High quality on-the-fly transformations of office documents using
   OpenOffice.org.

 * Flexible metadata handling

This package is an umbrella package that brings all other psj-related
packages together.

Currently, the whole thing consists of three packages:

 * ``psj.content`` (content types with extended metadata handling)

 * ``psj.policy`` (provides mainly office-document transformations using
   OpenOffice.org)

 * ``psj.site`` (this package).


This package creates a vanilla psj-site with the required scripts to
start, stop and maintain the site.

`psj` relies on the content management framework Plone. Visit

   http://www.plone.org/

to learn more about Plone.

Plone itself is backed up by Zope, an open source application
framework of upper-level quality and reliability. See

   http://www.zope.org/

to learn more about Zope.


Prerequisites
*************

You need the following things to install this package:

- **Python 2.4**

  Currently Python 2.4 is needed to run Zope (Plone and psj). You can
  find out, whether you have Python 2.4 installed by opening a shell
  and entering::

    $ python -V

  This should give you something like::

    Python 2.4.3

  Note, that the whole thing won't work with Python <= 2.3 nor with
  newer versions (>= 2.5).


- **`easy_install` and Python `setuptools`**

  If you don't have `easy_install` already available, you can find the
  script to set it up on the `PEAK EasyInstall page` at:

    http://peak.telecommunity.com/DevCenter/EasyInstall#installing-easy-install

  You need to download `ez_setup.py`, which is available at:

    http://peak.telecommunity.com/dist/ez_setup.py

  Then, you run it like this to install ``easy_install`` into your
  system Python::

    $ sudo python2.4 ez_setup.py

  This will make ``easy_install-2.4`` available to you.

  Then you can install the Python ``setuptools`` simply by entering::

    $ sudo easy_install-2.4 setuptools


- **A C-compiler**

  This is needed for compilation of the Zope 2 core elements. On Linux
  systems you normally have the Gnu C compiler `gcc` available.


- **PIL**

  The Python Imaging Library must be installed in your Python
  path. You can check, whether this is true by opening a shell and
  entering::

     $ python2.4 -c "import PIL"

  If you get no output at all, everything is fine. If you get a
  complaint like this::

     Traceback (most recent call last):
       File "<string>", line 1, in ?
     ImportError: No module named PIL

  then you have to install PIL before you proceed. PIL is available
  from

     http://www.pythonware.com/products/pil/

  Please follow the instructions given in the package.

You do *not* need to have a version of Plone or Zope already
installed. Instead, the build process will grab, configure and install
all other packages needed from the web.

  
Installation
************

First, make sure your system meets the requirements mentioned above.

`psj` uses a `zc.buildout`-driven installation process, that has to be
initialized first. Because ``buildout`` needs a fairly recent version
of ``setuptools``, you should update your version of it::

    $ sudo easy_install -U setuptools

This brings ``setuptools`` to the newest version available.

Now, we are ready to go. Bootstrap the initial buildout environment::

    $ python2.4 bootstrap/bootstrap.py

and run the buildout command::

    $ bin/buildout

Lots of stuff will be downloaded, compiled and installed here.

Note that if you have more than one sandbox for a Zope-based web
application, it will probably make sense to share the eggs between the
different sandboxes.  You can tell zc.buildout to use a central eggs
directory by creating ``~/.buildout/default.cfg`` with the following
contents::

    [buildout]
    eggs-directory = /home/bruno/buildout-eggs

If you happen to change the values in `buildout.cfg`, you have to
'rebuild' the environment by running ``bin/buildout`` again.


Running the site
****************

You can start Zope, Plone and psj with the following command::

  $ bin/instance start

This will start the server process and send it back in the
background. Stop the server with::

  $ bin/instance stop

If you do not want the server process to detach from the running
terminal, you can start it like this::

  $ bin/instance fg

In this case you can stop the server by pressing CTRL-C.

Do::

  $bin/instance --help

to get a complete list of things you can do with the start script.


Login
*****

After starting the server, you can reach it with your browser at

  http://localhost:8080/

To log into the site, go to 

  http://localhost:8080/manage

and enter the credentials as in buildout.cfg. By default the username
and password are both ``admin``.

This way you reach the Zope Management Interface (ZMI), where you can
manage your running Zope instance.

