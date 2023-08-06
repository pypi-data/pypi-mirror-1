Documentation for repoze.annotea
================================

.. topic:: Overview

   :mod:`repoze.annotea` implements the server side of the W3C Annotea_
   specification for RDF-based annotations on content, using
   :mod:`repoze.bfg` as the underlying framework for the application.

   The specification consists of two parts: an ``HTTP``-based protocol
   (see Annotea_Protocol_), specifying how clients interact with annotation
   servers to add, update, remove and query annotations;  and an
   ``RDF``-based language (see Annotea_Schema_), describing individual
   annotations.


.. toctree::
   :maxdepth: 2


Installation
------------

The recommended way to install the application is to put it into its own
virtualenv_, as follows::

  $ /path/to/virtualenv --no-site-packages /path/to/annotea
  $ cd /path/to/annotea
  $ bin/easy_install \
    -i http://dist.repoze.org/lemonade/dev/simple repoze.annotea


Create an instance::
   
  $ bin/paster create -t annotea

.. note:: The 'paster create' is "science fiction", and will be added later.

Edit the ``etc/annotea.ini`` script as desired, e.g., to change
the port number for the server.


Running the Server
------------------

To start the server::

  $ bin/annotea start

To stop the server::

  $ bin/annotea stop

.. note:: This 'annotea' script is "science fiction", and will be added later.
   At the moment, run it via the stock Paste metchanism, e.g.,
   'bin/paster serve annotea.ini`


Making Annotations
------------------

:mod:`repoze.annotea` has been tested primarily with the annozilla_ plugin
for Mozilla / Firefox.  Other Annotea_clients_ may also work:  please
try them out and let us know.

To configure annozilla_ to use your server:

#. Install the plugin and its dependent plugins into a browser profile.

#. On the "Tools" menu, select "Add-ons".

#. On the dialog, click on the "Annozilla" entry, then click the
   "Preferences" buton.

#. On the "Server Options" tab, click the "Edit Server Options" button.
  
#. Click the "New" button, and fill out the URL and authentication
   information for your server.  Click "OK".

#. At the bottom of the dialog, paste your server's URI as the "Default
   Post Server", and click "OK".

Exporting your annotations
---------------------------

To dump your annotation data (e.g., prior to moving it to another annotea
server), use the ``import_annotations`` script::

  $ /path/to/annotea/bin/export_annotations > /tmp/exported_annotations.rdf

To see the available command-line options::

  $ /path/to/annotea/bin/export_annotations --help


Bulk Loading Annotations
------------------------

To load exported RDF from another annotea server, use the
``import_annotations`` script::

  $ /path/to/annotea/bin/import_annotations < /tmp/exported_annotations.rdf

To see the available command-line options::

  $ /path/to/annotea/bin/import_annotations --help

.. note:: The 'import_annotations' script  is "science fiction", and will
   be added later.


Reporting Bugs
--------------

Please report any bugs to the
`repoze-dev mailing list <mailto:repoze.dev@lists.repoze.org>`_, or
ask for help on the `#repoze IRC channel <irc://irc.freenode.net/#repoze>`_ .


References
----------

.. _Annotea: http://www.w3.org/2001/Annotea/

.. _Annotea_Clients: http://www.w3.org/2001/Annotea/Projects#clients

.. _Annotea_Protocol: http://www.w3.org/2002/12/AnnoteaProtocol-20021219

.. _Annotea_Schema: http://www.w3.org/2000/10/annotation-ns#

.. _annozilla: http://annozilla.mozdev.org/

.. _virtualenv: http://pypi.python.org/pypi/virtualenv

.. target-notes:: 
