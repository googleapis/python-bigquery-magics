.. include:: README.rst

.. note::

   Because the BigQuery client uses the third-party :mod:`requests` library
   by default and the BigQuery-Storage client uses :mod:`grpcio` library,
   both are safe to share instances across threads.  In multiprocessing
   scenarios, the best practice is to create client instances *after*
   :class:`multiprocessing.Pool` or :class:`multiprocessing.Process` invokes
   :func:`os.fork`.

More Examples
~~~~~~~~~~~~~

.. toctree::
  :maxdepth: 2

  magics
  Official Google BigQuery Magics Tutorials <https://cloud.google.com/bigquery/docs/visualize-jupyter>


Migration Guide
---------------

Migrating from the ``google-cloud-bigquery``, you need to run the ``%load_ext bigquery-magics``
magic in a Jupyter notebook cell.

.. toctree::
    :maxdepth: 2


Changelog
---------

For a list of all ``bigquery-magics`` releases:

.. toctree::
  :maxdepth: 2

  changelog
