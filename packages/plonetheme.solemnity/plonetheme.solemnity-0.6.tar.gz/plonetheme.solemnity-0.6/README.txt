Introduction
============

An installable theme for Plone 3.0 based on the solemnity_ theme by `Six Shooter Media`_.

.. _solemnity: http://www.sixshootermedia.com/ostemplates/solemnity/
.. _`Six Shooter Media`: http://www.sixshootermedia.com/



Buildout Installation
=====================

Add the following code to your buildout.cfg::

  [buildout]
  ...
  eggs =
      ...
      plonetheme.solemnity
      ...

  ...
  [instance]
  ...
  zcml =
      ...
      plonetheme.solemnity
  ...