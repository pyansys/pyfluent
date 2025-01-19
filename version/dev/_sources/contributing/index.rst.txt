.. _ref_contributing:

========================
Contributing to PyFluent
========================

.. toctree::
   :maxdepth: 1
   :hidden:

   environment_variables

General guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar with
this guide, paying particular attention to the `Coding Style
<https://dev.docs.pyansys.com/coding-style/index.html#coding-style>`_ topic, before
attempting to contribute to PyFluent.
 
The following contribution information is specific to PyFluent.

Clone the repository
--------------------
Follow the steps in the Development Installation section of :ref:`ref_installation` 
to set PyFluent up in development mode.

Run unit tests
--------------

To run the PyFluent unit tests, execute the following command in the root
(``pyfluent``) directory of the repository:

.. code:: console

    pip install ansys-fluent-core[tests]
    python -m pytest -n 4 --fluent-version=25.1

You can change the Fluent version by replacing ``25.1`` with the version you want to test.

Build documentation
-------------------
To build the PyFluent documentation locally, run the following commands in the root
(``pyfluent``) directory of the repository:

.. code:: console

    pip install ansys-fluent-core[docs]
    cd doc
    make html

After the build completes, the HTML documentation is located in the
``_build/html`` directory. You can load the ``index.html`` file in
this directory into a web browser.

You can clear all HTML files from the ``_build/html`` directory with:

.. code::

    make clean

Post issues
-----------
Use the `PyFluent Issues <https://github.com/ansys/pyfluent/issues>`_ page to
submit questions, report bugs, and request new features.


Adhere to code style
--------------------
PyFluent is compliant with the `PyAnsys code style
<https://dev.docs.pyansys.com/coding-style/index.html>`_. It uses the tool
`pre-commit <https://pre-commit.com/>`_ to check the code style. You can
install and activate this tool with:

.. code:: bash

   python -m pip install pre-commit
   pre-commit install

You can then use the ``style`` rule defined in ``Makefile`` with:

.. code:: bash

   make style

Or, you can directly execute `pre-commit <https://pre-commit.com/>`_ with:

.. code:: bash

    pre-commit run --all-files --show-diff-on-failure
