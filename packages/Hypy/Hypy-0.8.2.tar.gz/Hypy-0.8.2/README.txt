====
Hypy
====

.. sidebar:: Download

    Download the `latest source`_ or `browse the source`_.  No matter how
    you choose to install Hypy, you will have to install `Hyper
    Estraier`_ first.

.. _latest source: http://hypy-source.goonmill.org/archive/tip.tar.gz

.. _browse the source: http://hypy-source.goonmill.org/file/tip/

.. sidebar:: Docs

    `Reference (API) documentation <http://goonmill.org/hypy/apidocs/>`_  See
    `Other Reference Docs`_ (below on this page) for even more stuff.

.. image:: /static/hypylogo.png

Hypy is a fulltext search interface for Python applications.  Use it to index
and search your documents from Python code.

Hypy is based on the estraiernative bindings by Yusuke Yoshida.

The estraiernative bindings are, in turn, based on Hyper Estraier by Mikio
Hirabayashi.

README
------

Installation: Ubuntu Users
~~~~~~~~~~~~~~~~~~~~~~~~~~
Hypy is hosted on Launchpad, and has a launchpad PPA.  This is arguably the
easiest way to install the software if you are an Ubuntu user.

Add the following lines to the end of ``/etc/apt/sources.list``.  You can
also paste these lines in to System > Administration > Software Sources >
Third-Party Software.

(intrepid)
::

    deb http://ppa.launchpad.net/corydodt/ubuntu intrepid main
    deb-src http://ppa.launchpad.net/corydodt/ubuntu intrepid main

(or hardy)
::

    deb http://ppa.launchpad.net/corydodt/ubuntu hardy main
    deb-src http://ppa.launchpad.net/corydodt/ubuntu hardy main

Then::

    sudo apt-get update
    sudo apt-get install python-hypy

All dependencies including Hyper Estraier will be auto-fetched for you, and
you will get automatic updates when I publish them.


Installation
~~~~~~~~~~~~
First things first.  Hypy depends on `Hyper Estraier`_.

Source code and a binary installer of Hyper Estraier for Windows can be found at
the `Hyper Estraier`_ website.

.. _Hyper Estraier: http://hyperestraier.sourceforge.net/

Linux users can probably install binary packages using their favorite package
manager.  You will need these:

* hyperestraier runtime
* libestraier headers and object code
* libqdbm headers and object code
* Python headers and object code, natch

If you are using Ubuntu, you can get all the build dependencies with this command
::

    sudo apt-get install hyperestraier libestraier-dev libqdbm-dev python-dev

I. easy_install or pip method
=============================
With setuptools (Ubuntu: sudo apt-get install python-setuptools), you can
install Hypy without even downloading it first, by using
::

    sudo easy_install hypy

If you have pip_, you should use that
::

    sudo pip install hypy

.. _pip: http://pip.openplans.org/


II. source method
=================
::

    python setup.py build; sudo python setup.py install

Optionally, run ``make tests`` in the source directory to see the unit tests
run.
 

Quick Start 
~~~~~~~~~~~
You can get an instant "oh I get it!" fix by looking inside the "examples"
directory distributed with this software.

- `gather.py`_ demonstrates how to index documents into a collection

- `search.py`_ demonstrates how to search for documents in an existing collection

.. _gather.py: http://hypy-source.goonmill.org/file/tip/examples/gather.py
.. _search.py: http://hypy-source.goonmill.org/file/tip/examples/search.py


Other Reference Docs
~~~~~~~~~~~~~~~~~~~~
If you can't find what you need in the `API docs`_ you should try one of the
following:

* The Hyper Estraier `User's Guide`_ describes the search syntax.  You plug
  this syntax into an instance of ``HCondition`` in Hypy.

* The `Hypy unit tests`_ contain a wealth of examples of search syntax,
  particularly in ``TestDatabase.test_queries`` and
  ``TestDatabase.test_condExtras``.  The tests cover 100% of the code in
  lib.py.  They have docstrings and comments; obscure things like skip and max
  searches and various attribute comparisons are covered.

.. _User's Guide: http://hyperestraier.sourceforge.net/uguide-en.html#searchcond
.. _Hypy unit tests: http://hypy-source.goonmill.org/file/tip/hypy/test_lib.py#l328
.. _API docs: http://goonmill.org/hypy/apidocs/


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
