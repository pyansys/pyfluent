.. _ref_installation:

============
Installation
============


PyFluent Installation
---------------------

PyFluent supports Python 3.10 through Python 3.13 on Windows, Mac OS and Linux.

PyFluent can be installed, along with all its optional dependencies, using:

.. code:: console

   pip install ansys-fluent-core


Development Installation
------------------------
The PyFluent source repository is available on GitHub. You can clone the repository and set up for local
development with the following commands:

.. code:: console

   git clone https://github.com/ansys/pyfluent.git
   cd pyfluent
   pip install pip -U
   pip install -e .
   python codegen/allapigen.py

Step-by-Step Explanation
~~~~~~~~~~~~~~~~~~~~~~~~

Clone the Repository
++++++++++++++++++++

.. code:: console

   git clone https://github.com/ansys/pyfluent.git
   cd pyfluent

These commands clone the PyFluent repository from GitHub to your local machine and navigate into
the repository directory.

Upgrade Pip
+++++++++++

.. code:: console

   pip install pip -U

This command upgrades pip to the latest version to ensure compatibility with the latest packages.

Install PyFluent in Editable Mode
+++++++++++++++++++++++++++++++++

.. code:: console

   pip install -e .

Installing with the -e option (editable mode) creates a symbolic link to the repository in the
``site-packages`` directory of your Python installation. This means any changes you make to the
PyFluent code are automatically reflected when you use PyFluent.

Generate Required API Classes
+++++++++++++++++++++++++++++

.. code:: console

   python codegen/allapigen.py

The full PyFluent package includes some required API classes that are auto-generated rather
than maintained under version control. This command runs the auto-generation script included
in the repository. Note that this step requires an Ansys Fluent installation.

By following these steps, you can set up PyFluent for local development, ensuring that any changes 
you make to the source code are immediately usable without needing to reinstall the package.

Fluent Installation
-------------------

To benefit fully from using PyFluent, you must have a licensed copy of Ansys Fluent installed.
All versions of PyFluent support Fluent 2022 R2 and later. 

PyFluent uses an environment variable to locate your Ansys installation.

On Windows, the Ansys installer sets the environment variable. For instance, the Ansys 2025 R1
installer sets the ``AWP_ROOT251`` environment variable to point to ``C:\Program Files\ANSYS Inc\v251``
if you accept the default installation location.

**On Linux, the environment variable is not set automatically.** It can be set for the
current user in the current shell session as follows:

.. code:: console

    export AWP_ROOT251=/usr/ansys_inc/v251

For this variable to persist between different shell sessions for the current user, the same
export command can instead be added to the user's ``~/.profile`` file.

For information on other ways of specifying the Fluent location for PyFluent, see :ref:`faqs_fluentloc` in :ref:`faqs`.


Additional PyFluent packages
----------------------------
In addition to the ``ansys-fluent-core`` package, you can install and use the
``pyfluent-parameteric`` and ``pyfluent-visualization`` packages:

- The `PyFluent-Parametric <https://parametric.fluent.docs.pyansys.com/>`_ package provides
  access to Fluent's parametric workflows.
- The `PyFluent-Visualization <https://visualization.fluent.docs.pyansys.com/>`_ package
  provides postprocessing and visualization capabilities that use `pyvista <https://docs.pyvista.org/>`_
  and `matplotlib <https://matplotlib.org/>`_ packages.
