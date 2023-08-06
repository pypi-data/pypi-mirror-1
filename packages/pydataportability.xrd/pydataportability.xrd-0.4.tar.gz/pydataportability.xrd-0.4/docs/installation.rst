.. _installing_chapter:

Installing :mod:`pydataportability.xrd`
=======================================

Before You Install
------------------

You will need `Python <http://python.org>`_ version 2.4 or better to
use :mod:`pydataportability.xrd`. 

You will also need to have :term:'setuptools' installed in order to run the
``easy_install`` command. Alternatively you can install
``pydataportability.xrd`` via :term:`buildout`.

Installing :mod:`pydataportability` on a UNIX System via setuptools
-------------------------------------------------------------------

It is advisable to install your project using :mod:`pydataportability.xrd`
into a :term:`virtualenv` in order to obtain isolation from any "system"
packages you've gotinstalled in your Python version (and likewise, to prevent
:mod:`pydataportability.xrd` or your project from globally installing versions
of packages that are not compatible with your system Python).

To set up a virtualenv, first ensure that :term:`setuptools` is installed.
Invoke ``import setuptools`` within the Python interpreter you'd like to run
:mod:`repoze.bfg` under:

.. code-block:: bash

  $ python
  Python 2.4.5 (#1, Aug 29 2008, 12:27:37) 
  [GCC 4.0.1 (Apple Inc. build 5465)] on darwin
  Type "help", "copyright", "credits" or "license" for more information.
  >>> import setuptools

If ``import setuptools`` does not raise an ``ImportError``, it means
that setuptools is already installed into your Python interpreter.  If
``import setuptools`` fails, you will need to install setuptools
manually.

If you are using a "system" Python (one installed by your OS
distributor or a 3rd-party packager such as Fink or MacPorts), you can
usually install a setuptools package using your system's package
manager.  If you cannot do this, or if you're using a self-installed
version of Python, you will need to install setuptools "by hand".
Installing setuptools "by hand" is always a reasonable thing to do,
even if your package manager already has a pre-chewed version of
setuptools for installation.

To install setuptools by hand, first download `ez_setup.py
<http://peak.telecommunity.com/dist/ez_setup.py>`_ then invoke it
using the Python interpreter you want to install setuptools into.

.. code-block:: bash

  $ sudo python ez_setup.py

Once this command is invoked, setuptools should be installed on your
system.  If the command fails due to permission errors, you may need
to be the administrative user on your system to successfully invoke
the script.  To remediate this, you may need to do:

.. code-block:: bash

  $ sudo python ez_setup.py

Installing the ``virtualenv`` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've got setuptools installed, you should install the
:term:`virtualenv` package.  To install the :term:`virtualenv` package
into your setuptools-enabled Python interpreter, use the
``easy_install`` command.

.. code-block:: bash

  $ easy_install virtualenv

This command should succeed, and tell you that the virtualenv package
is now installed.  If it fails due to permission errors, you may need
to install it as your system's administrative user.  For example:

.. code-block:: bash

  $ sudo easy_install virtualenv

Creating the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the :term:`virtualenv` package is installed in your Python, you
can actually create a virtual environment.  To do so, invoke the
following:

.. code-block:: bash
   :linenos:

   $ virtualenv --no-site-packages myenv
   New python executable in bfgenv/bin/python
   Installing setuptools.............done.

.. warning:: Using ``--no-site-packages`` when generating your
   virtualenv is *very important*. This flag provides the necessary
   isolation for running the set of packages required by your project.
   For instance sometimes a pre-installed package in the system Python
   installation will prevent your project from running properly. Using
   ``-no-site-packages`` will prevent this and will tell your environment
   to ignore any site wide packages.

.. warning:: If you're on UNIX, *do not* use ``sudo`` to run the
   ``virtualenv`` script.  It's perfectly acceptable (and desirable)
   to create a virtualenv as a normal user.

You should perform any following commands that mention a "bin"
directory from within the ``myenv`` virtualenv dir. Of course you can
also use any other name than ``myenv`` as the name for your virtualenv
environment.

Installing :mod:`pydataportability.xrd` into the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After you've got your ``myenv`` virtualenv installed, you may install
:mod:`pydataportability.xrd` itself using the following commands from within
the virtualenv (``myenv``) directory:

.. code-block:: bash
   :linenos:

   $ bin/easy_install -U pydataportabilty.xrd

.. warning:: Note carefully the ``-U`` flag. This tells setuptools to
   update an maybe already installed version. If you are installing this
   for the first time into your ``virtualenv`` then you of course can
   omit this flag.

This command will take longer than the previous ones to complete, as it
downloads and installs a number of dependencies.

Installing :mod:`pydataportability.xrd` on a Windows System
-----------------------------------------------------------

#. Install, or find `Python 2.5
   <http://python.org/download/releases/2.5.4/>`_ for your system.

#. Install the `Python for Windows extensions
   <http://sourceforge.net/projects/pywin32/files/>`_.  Make sure to
   pick the right download for Python 2.5 and install it using the
   same Python installation from the previous step.

#. Install latest `setuptools` into the Python you
   obtained/installed/found in the step above: download `ez_setup.py
   <http://peak.telecommunity.com/dist/ez_setup.py>`_ and run it using
   the ``python`` interpreter of your Python 2.5 installation using a
   command prompt:

   .. code-block:: bat

    c:\> c:\Python25\python ez_setup.py

#. Use that Python's `bin/easy_install` to install `virtualenv`:

   .. code-block:: bat

    c:\> c:\Python25\Scripts\easy_install virtualenv

#. Use that Python's virtualenv to make a workspace:

   .. code-block:: bat

     c:\> c:\Python25\Scripts\virtualenv --no-site-packages myenv

#. Switch to the ``myenv`` directory:

   .. code-block:: bat

     c:\> cd myenv

#. (Optional) Consider using ``bin\activate.bat`` to make your shell
   environment wired to use the virtualenv.

#. Use ``easy_install`` to install ``pydataportability.xrd``:

   .. code-block:: bat

     c:\myenv> Scripts\easy_install -U pydataportability.xrd


What Gets Installed
~~~~~~~~~~~~~~~~~~~

When you ``easy_install`` :mod:`pydataportability.xrd`, various Zope libraries,
elementtree and other pydataportability components are installed.

