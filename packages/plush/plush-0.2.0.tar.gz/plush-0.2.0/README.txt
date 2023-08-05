=====
Plush
=====

:author: Benoit Delbosc

:address: bdelbosc _at_ nuxeo.com

:version: Plush/0.2.0 **DRAFT**

:revision: $Id: README.txt 51224 2007-02-22 09:31:36Z bdelbosc $

:Copyright: (C) Copyright 2007 Nuxeo SAS (http://nuxeo.com).
            This program is free software; you can redistribute it and/or
            modify it under the terms of the GNU General Public License as
            published by the Free Software Foundation; either version 2 of
            the License, or (at your option) any later version.
            This program is distributed in the hope that it will be useful,
            but WITHOUT ANY WARRANTY; without even the implied warranty of
            MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
            General Public License for more details.
            You should have received a copy of the GNU General Public
            License along with this program; if not, write to the Free
            Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
            MA 02111-1307, USA.

:abstract: This document describes the usage of the Plush_. It is a is a
           simple interactive command line shell to inspect a Lucene_ indexes.

.. sectnum::    :depth: 1

.. contents:: Table of Contents


Introducing Plush
=================

What is Plush ?
---------------

Plush_ is PyLUcene SHell to play with a Lucene_ indexes interactively.

Main features:

* View store information.

* View indexes definition.

* Search using the Lucene_ `Query Parser Syntax`_.

* Sort result list.

* Browse by document number.

* Top term occurences for a field, matching a regex.

* Support PyLucene_ 1.9.1 and 2.0.0.

* Interactive shell emacs like command history and editing features.

* Command line tool and thus scriptable.

* Easy installation, no java required.

* Can load NXLucene_ analyzers.

* Plush is free software distributed under the `GNU GPL`_.

* Plush is written in python and can be easily customized.


Why using Plush_ instead of Luke_ ?

* Lucene_ indexes are on a remote server.

* You are using PyLucene_ no java available on the server.

* No X server available.

* You want to sort the result list.

* You want to have an idea of the search response time.

* You need to run command line scripts.

For other cases have a look to the great Luke_ tool.


Where to find Plush ?
=====================

Get the latest package from python `Cheese Shop`_.

Or use the bleeding edge ::

   svn co http://svn.nuxeo.org/pub/tools/plush/trunk plush


Installation
============

* You need python 2.4 (2.3 not tested) with the readline support
  (--enable-readline)

* Plush_ requires PyLucene_ which is easy to install using binaries.

  Here is an example on how to install the latest PyLucene_ 2.0.0-3 (Lucene_
  2.0.0-453447) on ubuntu::

    cd /tmp
    wget http://downloads.osafoundation.org/PyLucene/linux/ubuntu/PyLucene-2.0.0-3.tar.gz
    tar xzvf PyLucene-2.0.0-3.tar.gz
    cd PyLucene-2.0.0-3/
    sudo cp -r python/* /usr/lib/python2.4/site-packages/
    sudo cp -r gcj/* /usr/local/lib

  Visit the PyLucene_ site for other pre-built binaries.

* Plush_ is a pure python package that you can get from the Python `Cheese
  Shop`_ ::

    tar xzvf plush-X.Y.Z.tar.gz
    cd plush

  Install plush either with::

    sudo make install

  or using the pythonic way::

    python setup.py build
    sudo python setup.py install

Thats all no .jar nor java required.

Plush commands
==============

Plush_ commands begin with a backslash other inputs are traited as Lucene_ query.

::

  plush > \help
  Documented commands (type \help <topic>):
  ========================================
  close  describe_indexes  di    exit  history  open  quit  term   v
  d      describe_store    echo  help  nuxset   q     set   unset  view



Examples
--------
::

 $ plush
 plush
 Welcome to Plush 0.1.0, a Lucene interactive terminal.
 Using PyLucene 2.0.0-3 and Lucene 2.0.0-453447.

   Type: \open [INDEX_PATH]    to open a lucene store
         \?                    for help
         \q or ^D              to quit.

 plush> \open tmp/PyLucene-2.0.0-3/samples/index
 Opening store: /home/ben/tmp/PyLucene-2.0.0-3/samples/index

 plush> \d
 Directory info
 --------------
 * Directory path             : /home/ben/tmp/PyLucene-2.0.0-3/samples/index
 * Directory current version  : 1168939081493
 * Number of docs             : 578 (max doc num: 580)
 * Number of fields           : 3
 * Index last modified        : 2007-01-30T11:04:46
 * Index status               : unlocked
 * Has deletions              : YES
 * Directory implementation   : org.apache.lucene.store.FSDirectory

 plush> \di
 Index info
 ----------
 Found 3 fields for doc #579:
 * contents                     Stored Indexed Tokenized
 * name                         Stored Indexed
 * path                         Stored Indexed

 plush> foo -bar
 Searching: foo -bar
 ------------------------------------
   Default search index: contents
   Simple analyzer tokens: foo, bar
   Found 3 matching document(s) in 0.002s

 * 00) score: 0.56, doc_num: 218
   name: migrating-from-nuxmetadirectories.txt
   path: /home...migrating-from-nuxmetadirectories.txt

 * 01) score: 0.40, doc_num: 246
   name: creating-new-content-types.txt
   path: /home...creating-new-content-types.txt

 * 02) score: 0.16, doc_num: 184
   name: guidelines-user_interface.txt
   path: /home...guidelines-user_interface.txt

   Found 3 matching document(s) in 0.002s

 plush> \v 184
 Found 3 fields for doc #184
 contents                   S I T    : <snip>file content</snip>
 name                       S I      : guidelines-user_interface.txt
 path                       S I      : /home...guidelines-user_interface.txt

 plush> \v 184 ^name
 Found 3 fields for doc #184
 name                       S I      : guidelines-user_interface.txt

 plush> \set
   limit = 5
   select = name path
   default_field = contents
   sort_on =
   waterline =
   analyzer = Simple

 plush> \set sort_on contents
  It is not possible to sort on a tokenized field


 plush> \term contents
 Top 5 term occurences for field 'contents' matching '*'.
 occurences term
 ---------- ----
        455 http
        455 information
        452 more
        446 directory
        434 copy
 ---------- ----

 plush> \set limit 7
   limit key setted.

 plush> \term name \.txt$
 Top 7 term occurences for field 'name' matching '\.txt$'.
 occurences term
 ---------- ----
        449 README.txt
         13 DEPENDENCIES.txt
         13 refresh.txt
          6 TODO.txt
          5 INSTALL.txt
          5 LICENSE.txt
          3 COPYING.txt
 ---------- ----

 plush> ^D
 Bye

The command history is saved in the ~/.plush_history file.


Using NXLucene analyzers
------------------------

You can use the NXLucene_ analyzers by setting an environnement variable
``NXLUCENE_HOME`` that point to the path where the ``analyzers`` python
module can be loaded.

::

    $ export NXLUCENE_HOME=/usr/local/nxlucene/src/nxlucene
    $ plush
    NXLucene analyzers Loaded.
    ...
    plush> \set analyzer french
    Error: Invalid analyzer.
       Possible values are: nxfrench, nxsort, Whitespace, Keyword, nxstandard, German, Stop, French, Standard, Simple, nxurl, nxkeyword
    plush> \set analyzer nxfrench
    plush> l'½uvre d'art
    Searching: l'½uvre d'art
    ------------------------------------
    Default search index: contents
    nxfrench analyzer tokens: oeuvr, art
    ...

NXLucene_ analyzers are prefixed with ``nx``.


Troubles
========

* ImportError: No module named readline

  You need to compile your python with readline support which requires the
  readline-devel package ::

   ./configure --enable-readline


.. _Plush: http://public.dev.nuxeo.com/~ben/plush/
.. _PyLucene: http://pylucene.osafoundation.org/
.. _Lucene: http://lucene.apache.org/java/docs/index.html
.. _NXLucene: http://svn.nuxeo.org/trac/pub/browser/NXLucene/trunk/README.txt
.. _here: http://downloads.osafoundation.org/PyLucene/linux/debian/debian.txt
.. _`Cheese Shop`: http://www.python.org/pypi/plush
.. _`Query Parser Syntax`: http://lucene.apache.org/java/docs/queryparsersyntax.html
.. _Luke: http://www.getopt.org/luke/
.. _epydoc: http://epydoc.sourceforge.net/
.. _`GNU GPL`: http://www.gnu.org/licenses/licenses.html

.. Local Variables:
.. mode: rst

.. <!-- Local Variables: -->
.. <!-- coding: utf-8 -->
.. <!-- End: -->
