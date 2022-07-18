Options
=========

You could use

.. code:: python

    from sinophone import options as sinoptions

    sinoptions.repr_lang = "wuu-Hant"  # Wu Chinese in Traditional Sinographs
    sinoptions.<option> = <value>

to set ``sinophone`` package options.

To access objects in the submodule with the same name (which you would unlikely need to), use ``from sinophone.options import <object>``.


Interface for options
---------------------

.. autodata:: sinophone.options
    :noindex:

    Abbreviation of ``sinophone.options.options``.


Default values used in ``options``
----------------------------------

.. automodule:: sinophone.options
    :members:
    :show-inheritance:
    :inherited-members:
    :exclude-members: options


Indices
-------

* :ref:`genindex`
* :ref:`modindex`
