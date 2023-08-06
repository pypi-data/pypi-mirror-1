Introduction
============

An installable theme for Plone 3.0 based on the Mimbo_ theme by `Darren Hoyt`_.

.. _Mimbo: http://www.darrenhoyt.com/2007/08/05/wordpress-magazine-theme-released
.. _`Darren Hoyt`: http://www.darrenhoyt.com/



Buildout Installation
=====================

Add the following code to your buildout.cfg::

  [buildout]
  ...
  eggs =
      ...
      plonetheme.mimbo
      ...

  ...
  [instance]
  ...
  zcml =
      ...
      plonetheme.mimbo
  ...