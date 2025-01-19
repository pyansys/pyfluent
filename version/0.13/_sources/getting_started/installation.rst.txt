.. _installation:

============
Installation
============

The ``ansys-fluent-core`` package supports Python 3.7 through
Python 3.10 on Windows and Linux.

.. note::
   This page provides information for quickly installing and launching
   the ``ansys-fluent-core`` package. Additional PyFluent packages, which
   are described later on this page, can also be installed. For
   information on installing all PyFluent packages in a virtual environment,
   see :ref:`faqs_install` in :ref:`faqs`.

Install the package
-------------------
Install the latest ``ansys-fluent-core`` package from
`PyPi <https://pypi.org/project/ansys-fluent-core/>`_ with this code:

.. code::

   pip install ansys-fluent-core

If you plan on doing local *development* of PyFluent with Git, install the
latest ``ansys-fluent-core`` package with this code:

.. code:: console

   git clone https://github.com/pyansys/pyfluent.git
   cd pyfluent
   pip install pip -U
   pip install -e .
   python codegen/allapigen.py  # Generates the API files


Any changes that you make locally are reflected in your setup after you restart
the Python kernel.

Launch Fluent
-------------
To launch Fluent from PyFluent, use the :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`
method:

.. code:: python

  import ansys.fluent.core as pyfluent
  solver = pyfluent.launch_fluent(precision="double", processor_count=2, mode="solver")
  solver.health_check_service.is_serving

To locate the latest Fluent installation, PyFluent automatically uses the ``AWP_ROOT<ver>``
environment variable, where ``<ver>`` is the three-digit format for the release.
For example, ``AWP_ROOT231`` is the environment variable for the 2023 R1 release. 

On a Windows system, this environment variable is configured when a release is installed.

On a Linux system, you must configure this environment variable to point to the absolute
path of the installed release. For example, for the 2023 R1 release, you would set
the ``AWP_ROOT231`` environment variable to point to an absolute location such as
``/apps/ansys_inc/v231``.

For information on other ways of specifying the Fluent location for PyFluent, see :ref:`faqs_fluentloc` in :ref:`faqs`.

Once Fluent is active, you can use the ``solver_session.tui`` interface to send
Fluent TUI commands to PyFluent. For example, this code reads a case file, updates a
setting, and iterates the solver:

.. code:: python

  solver.tui.file.read_case('elbow.cas.h5')
  solver.tui.define.models.unsteady_2nd_order("yes")
  solver.tui.solve.initialize.initialize_flow()
  solver.tui.solve.dual_time_iterate(2, 3)

If you want to interact with the Fluent GUI (graphical user interface), pass ``show_gui=True``
to the :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>` method:

.. code:: python

  session = pyfluent.launch_fluent(precision="double", processor_count=2, show_gui=True, mode="solver")

If you want to print the debug information for development, set the following
environment variable:

.. code:: python

  pyfluent.set_log_level('DEBUG') # for development, by default only errors are shown


Additional PyFluent packages
----------------------------
In addition to the ``ansys-fluent-core`` package, you can install and use the
``pyfluent-parameteric`` and ``pyfluent-visualization`` packages:

- The `PyFluent-Parametric <https://parametric.fluent.docs.pyansys.com/>`_ package provides
  access to Fluent's parametric workflows.
- The `PyFluent-Visualization <https://visualization.fluent.docs.pyansys.com/>`_ package
  provides postprocessing and visualization capabilities that use `pyvista <https://docs.pyvista.org/>`_
  and `matplotlib <https://matplotlib.org/>`_ packages.
