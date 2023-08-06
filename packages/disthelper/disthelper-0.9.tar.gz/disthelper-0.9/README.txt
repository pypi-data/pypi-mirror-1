===========
disthelper
===========

.. contents:: :local:

Introduction
============

disthelper is a command line tool that helps you manage a Python distribution.  You may want to create Python scripts to automate common maintenance tasks for your project.  But where do you put them?  Your `setup.py`_ script.  You can think of setup.py as a "make" tool for Python, although it's more like how `Ian Bicking describes it`_ and less like an `actual make tool`_ with targets and dependencies.  For example, if you wrote a script to build your project docs and another to upload them, you could run these commands like this from your project directory::

    python setup.py build_docs upload_docs

What it does
============

disthelper just automates the use of distutils_ so you don't have to think about how to `create a custom setup.py command`_.  It sets up the module / submodule structure, edits your setup.cfg, and adds new command modules as you request them.  disthelper doesn't do anything you couldn't do by hand.

.. _create a custom setup.py command: http://docs.python.org/dist/node32.html
.. _actual make tool: http://www.gnu.org/software/make/manual/make.html#Overview
.. _Ian Bicking describes it: http://blog.ianbicking.org/pythons-makefile.html
.. _setup.py: http://docs.python.org/dist/setup-script.html
.. _creating custom distutils commands: http://peak.telecommunity.com/DevCenter/setuptools#adding-commands
.. _distutils: http://docs.python.org/dist/dist.html
.. _setuptools: http://pypi.python.org/pypi/setuptools

Install
=======

You can easy_install_ it::

    easy_install disthelper

.. _source: http://disthelper.googlecode.com/svn/trunk/#egg=disthelper-dev
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall

Create a command
================

disthelper is implemented as a `Paste`_ extension.  Let's say you want to create this ``build_docs`` command I mentioned.  cd into your project directory and type::

    $ paster distcmd build_docs
    | ...
    | ./foo/distcmds/build_docs.py
    | ...is ready to edit
    | run as:
    |     python setup.py build_docs
    | 

If you don't already have a Python package it will prompt you for its name.  Assuming you named your package ``foo``, you should see the following layout::
    
    $ ls -R
    | foo             setup.cfg       setup.py
    | 
    | ./foo:
    | __init__.py     distcmds
    | 
    | ./foo/distcmds:
    | __init__.py     build_docs.py

Your command is ready to run::

    $ python setup.py build_docs --help
    | Global options:
    |   --verbose (-v)  run verbosely (default)
    |   --quiet (-q)    run quietly (turns verbosity off)
    |   --dry-run (-n)  don't actually do anything
    |   --help (-h)     show detailed help message
    | 
    | Options for 'build_docs' command:
    |   --long-option (-l)        <help>
    |   --other-long-option (-o)  <help>
    | 
    | usage: setup.py [global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...]
    |    or: setup.py --help [cmd1 cmd2 ...]
    |    or: setup.py --help-commands
    |    or: setup.py cmd --help
    | 

However, it doesn't do anything useful yet so get to it!

.. _Paste: http://pythonpaste.org/

My command disappeared, what do I do?
=====================================

Unfortunately, distutils will completely ignore any ImportError in your command so one day your command might simply disappear.  To check that your command is set up correctly, run::

    $ paster distcmd build_docs --check


.. The distutils Command class
   ===========================
   
Other make like tools
=====================

disthelper isn't designed for complex builds, dependency management, etc, it just helps you create maintenance scripts.  You may want to check out...

- Vellum_

  - Vellum is a simple build tool like make but written in Python using a simple yet flexible YAML based format.

- SCONS_
  
  - A software construction tool

- `zc.buildout`_

  - System for managing development buildouts

.. _Vellum: http://www.zedshaw.com/projects/vellum/index.html
.. _SCONS: http://www.scons.org/
.. _zc.buildout: http://pypi.python.org/pypi/zc.buildout/