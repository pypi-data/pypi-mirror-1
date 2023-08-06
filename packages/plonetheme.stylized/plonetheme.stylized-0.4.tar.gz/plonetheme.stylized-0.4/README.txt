Introduction
============

An installable theme for Plone 3.0 based on the stylized_ theme by `NodeThirtyThree`_.

.. _stylized: http://www.freecsstemplates.org/preview/stylized
.. _`NodeThirtyThree`: http://www.nodethirtythree.com/



Buildout Installation
=====================

Add the following code to your buildout.cfg::

  [buildout]
  ...
  eggs =
      ...
      plonetheme.stylized
      ...

  ...
  [instance]
  ...
  zcml =
      ...
      plonetheme.stylized
  ...