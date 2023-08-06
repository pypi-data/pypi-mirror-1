Introduction
------------

Provides a configlet to set the allowed content types for Plone in a n x n
Matrix.


Installation
------------

These instructions assume that you already have a Plone 3 buildout that's built
and ready to run.

Edit your buildout.cfg file and look for the eggs key in the instance section.
Add collective.allowtypes to that list. Your list will look something like this::

    eggs =
        ${buildout:eggs}
        ${plone:eggs}
        collective.allowtypes

In the same section, look for the zcml key. Add collective.allowtypes here,
too::

    zcml = collective.allowtypes


Usage
-----

A control panel configlet will be installed

http://localhost:8080/plone/plone_control_panel


::
 vim: set ft=rst ts=4 sw=4 expandtab tw=78 :
