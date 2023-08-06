Introduction
============

A the moment lfcs-kel provides one template to create new LFC application. More
might follow.

Usage
=====

Install lfc-skel using easy_install::

    $ easy_install lfc_skel

You should then be able to see a new lfc_app template available::

    $ paster create --list-templates

       Available templates:
         ...
         lfc_app:                   Template for a basic LFC application
         ...

To create a new LFC application just type the following and answer the
questions::

    $ paster create -t lfc_app

Changes
=======

1.0 alpha 1 (2010-01-26)
------------------------

* Initial public release