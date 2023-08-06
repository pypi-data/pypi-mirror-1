Introduction
============

An installable theme for Plone 3.0

Buildout Installation
=====================

Add the following code to your buildout.cfg::

  [buildout]
  ...
  eggs =
      ...
      plonetheme.rcom
      ...

  ...
  [instance]
  ...
  zcml =
      ...
      plonetheme.rcom
  ...