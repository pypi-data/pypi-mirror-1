OFolder
=======

  An OFolder contains an ordered sequence of objects.

  Besides the ordering, it behaves identical to a Folder.

  You can reorder the objects by assigning new order numbers (these
  are float values) and then press 'reorder'.

History
=======

 1.0.1
   * Zope 2.12 dropped ``ZClasses`` -- make ``ZClass`` base class registration conditional
   * Zope 2.12 stupidly deprecated import of ``InitializeClass`` and ``DTMLFile`` from ``Globals`` -- avoid deprecation messages
