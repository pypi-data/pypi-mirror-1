====
Hypy
====

.. sidebar:: Download

    Download the `latest source`_ or `browse the source`_ or get the `latest
    official release`_.

.. _latest source: http://hypy-source.goonmill.org/archive/tip.tar.gz
.. _latest official release: http://pypi.python.org/pypi/Hypy/0.8.2
.. _browse the source: http://hypy-source.goonmill.org/file/tip/

.. sidebar:: Docs

    `Reference (API) documentation <http://goonmill.org/hypy/apidocs/>`_.   Or
    maybe `Quick Start`_ (below on this page).  You probably want the
    `examples`_ though, knowing you.

.. _examples: examples.tsw

.. image:: /static/hypylogo.png

Hypy is a fulltext search interface for Python applications.  Use it to index
and search your documents from Python code.

Hypy is based on the estraiernative bindings by Yusuke Yoshida.

The estraiernative bindings are, in turn, based on Hyper Estraier by Mikio
Hirabayashi.

README
------

Installation: Ubuntu using APT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Hypy is hosted on Launchpad, and has a launchpad PPA.  This is arguably the
easiest way to install the software if you are an Ubuntu user.

Add the following lines to the end of ``/etc/apt/sources.list``.  You can
also paste these lines in to System > Administration > Software Sources >
Third-Party Software.

(intrepid)
::

    deb http://ppa.launchpad.net/corydodt/ppa/ubuntu intrepid main
    deb-src http://ppa.launchpad.net/corydodt/ppa/ubuntu intrepid main

(or hardy)
::

    deb http://ppa.launchpad.net/corydodt/ubuntu hardy main
    deb-src http://ppa.launchpad.net/corydodt/ubuntu hardy main

Then::

    sudo apt-get update
    sudo apt-get install python-hypy

All dependencies including Hyper Estraier will be auto-fetched for you, and
you will get automatic updates when I publish them.


Installation: Non-Ubuntu
~~~~~~~~~~~~~~~~~~~~~~~~

If you don't have Ubuntu or don't intend to use the PPA, you will need to
(a) install Hyper Estraier, then (b) install Hypy.

**Don't be intimidated by how long this section is; check your distribution
first for binary packages!  Windows users, there's a link for you below.
Everyone who likes things to be complicated, read on.**

Installing Hyper Estraier on Windows
====================================

If you are using Windows, a binary installer for `Windows Hyper Estraier`_ can
be had.  **You must still install Hypy, perhaps with easy_install, so see
below.**

.. _Windows Hyper Estraier: http://hyperestraier.sourceforge.net/win/

Installing Hyper Estraier (dev packages) with a package manager
===============================================================

Linux users can probably install binary packages using their favorite package
manager.  You will need these:

* hyperestraier runtime
* libestraier headers and object code
* libqdbm headers and object code
* Python headers and object code, natch

If you are using Ubuntu (and for some reason you won't just use the PPA
above), you can get all the build dependencies with this command::

    sudo apt-get install hyperestraier libestraier-dev libqdbm-dev python-dev

Installing Hyper Estraier from Source
=====================================

Instructions for building and `installing Hyper Estraier`_ can be found on
that site.  It is a standard configure/make/make install process, but you must
make sure to download all the required files.  See the Hyper Estraier
installation page for details.

.. _installing Hyper Estraier: http://hyperestraier.sourceforge.net/intro-en.html#installation

Then: Install Hypy with easy_install or pip
===========================================
With setuptools (Ubuntu: sudo apt-get install python-setuptools), you can
install Hypy without even downloading it first, by using
::

    sudo easy_install hypy

If you have pip_, you should use that
::

    sudo pip install hypy

.. _pip: http://pip.openplans.org/


... or: Install Hypy from tarball
=================================

Get one of the tarballs `linked`_ at the top of the page.

::

    tar xvfz hypy.tar.gz; cd Hypy-*
    python setup.py build; sudo python setup.py install

Optionally, run::

    make tests

in the source directory to see the unit tests run.

.. _linked: Hypy_
 

Quick Start 
~~~~~~~~~~~
You can get an instant "oh I get it!" fix by looking inside the "examples"
directory distributed with this software.

Index documents into a collection (see `gather.py`_ for the complete program)::

    ...

    db = HDatabase()
    db.open('casket', 'w')
    # create a document object
    doc = HDocument(uri=u'http://estraier.gov/example.txt')
    ...

Search for documents in an existing collection (see `search.py`_ for the
complete program)::

    ...

    # create a search condition object
    cond = HCondition(u'lull*')
    # get the result of search
    result = db.search(cond)
    # iterate the result
    for doc in result:
    ...

.. _gather.py: http://hypy-source.goonmill.org/file/tip/examples/gather.py
.. _search.py: http://hypy-source.goonmill.org/file/tip/examples/search.py


Hey, I need Even More Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OK. 

Here are `even more examples`_.  (Find this in the doc/ directory if you
unpacked the tarball and are reading this from there.)

.. _even more examples: examples.tsw


Read This! - Unicode
~~~~~~~~~~~~~~~~~~~~
To make the transition to Python 3.0 easier, and because it is a good idea,
Hypy requires Unicode objects in all of its APIs.

*WRONG*
::

  >>> d = HDocument(uri='http://pinatas.com/store.html') # byte string!
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/usr/lib/python2.5/site-pacakges/hypy/lib.py", line 291, in __init__
      raise TypeError("Must provide uri as unicode text")
  TypeError: Must provide uri as unicode text

*RIGHT*
::
 
  >>> d = HDocument(uri=u'http://pinatas.com/store.html') # unicode :-)
  >>> d.addText(u'Olé')
  >>> d[u'@title'] = u'Piñata Store'  # attributes are also unicode

Because of this change, and some other minor, Python-enhancing differences
between the APIs, I have deliberately renamed all the classes and methods
supported by Hypy, to prevent confusion.  If you know Python and are already
familiar with Hyper Estraier, you should now visit the `API docs`_ to learn
the new names of functions.  In general, though, "est_someclass_foo_bar" takes
a byte string in Hyper Estraier, but becomes "HSomeClass.fooBar" in Hypy and
takes Unicode text.

.. _API docs: api/

What's not Supported in Hypy vs. Hyper Estraier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Hyper Estraier implements a version of federated search which is supported by
its APIs such as merge, search_meta and eclipse.  If I hear a compelling use case
or receive patches with unit tests, I may add support for these APIs.  This is
not a hard thing to do, I just have no use for it myself, so I am reluctant to
promise to maintain it unless someone else really needs it.


Contributing and Reporting Bugs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Hypy has a `bug tracker <https://bugs.launchpad.net/hypy>`_ on Launchpad.

For more information on contributing, including the URL of the source
repository for Hypy, go to `DevelopmentCentral
<http://wiki.goonmill.org/DevelopmentCentral>`_ on the wiki_.

.. _wiki: http://wiki.goonmill.org/

It bears emphasizing that **bugs with reproducible steps, patches and unit
tests** (in that order) **get fixed sooner**.


License
~~~~~~~
LGPL 2.1

Hypy (c) Cory Dodt, 2008.

estraiernative (c) Yusuke Yoshida.
