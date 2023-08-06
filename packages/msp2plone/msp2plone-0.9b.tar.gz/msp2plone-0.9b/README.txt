Introduction
============

An M$ Project (or better: Merlin) to Plone "eXtreme Management" importer.

This is a standalone script which uses **wsapi4plone** to create content 
in Plone.

Installation
------------

Just install the egg -- but be sure thet **lxml** can be properly installed.

Usage
-----

::

    Usage: msp2plone [options]

    Options:
      -h, --help            show this help message and exit
      -u URL, --url=URL     The URL to the Plone site.
      -f FILENAME, --file=FILENAME
                            The file name to the MS Project XML file
      -p PATH, --path=PATH  The root path to the container to create the XM
                            project in.
      -m MODE, --mode=MODE  Either 'merlin' or 'ms project'


URL Format
~~~~~~~~~~

The URL format is as follows::

  https://<<user>>:<<pass>>@<<somehost>>:<<port>>/<<plonesite>>

For example::

  http://admin:admin@127.0.0.1:8080/plone


Conventions
-----------

In the default mode ("ms project"), every top-level node of the MS Project file
will become a **Project**, nodes below that will become **Iterations** and
**Stories**, respectively.

If the *Note* text of a Story-Level node matches, **Tasks** will be created.
For this to work, the keyword "task: " must be there, as follows::

  This is a sample Story text.

  Some additional Text.

  task: Frobnicate Whizbangs
  task: Kaboodle Whizbangs # 17 # alfred,josef
  task: Management Meeting # 8 # catbert

A story with the above text will get three tasks:

- task 1: Frobnicate Whizbangs, no estimate, assigned to nobody
- task 2: Kaboodle Whizbangs, estimate 17 hours, assigned to  alfred and josef
- task 3: Management Meeting, estimate 8 hours, assigned to catbert

GUI
---

None yet, sorry.

Links
-----

**SVN**
   https://msp2plone.googlecode.com/svn/tags/0.9b

**wsapi4plone**
   http://pypi.python.org/pypi?%3Aaction=search&term=wsapi4plone&submit=search


..  vim: set ft=rst ts=4 sw=4 expandtab tw=78 : 


