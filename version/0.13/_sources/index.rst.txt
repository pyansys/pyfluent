PyFluent documentation |version|
================================

.. toctree::
   :hidden:
   :maxdepth: 2

   getting_started/index
   user_guide/index
   api/index
   examples/index
   contributing

Introduction
------------
Ansys Fluent is a state-of-the-art computational fluid dynamics (CFD) software
package for modeling fluid flow, heat transfer, and chemical reactions in
complex geometries.

Fluent provides complete mesh flexibility, including the ability to solve your
flow problems using unstructured meshes that can be generated about complex
geometries with relative ease. Supported mesh types include:

- 2D triangular and quadrilateral
- 3D tetrahedral, hexahedral, pyramid, wedge, and polyhedral
- Mixed (hybrid)

Fluent also enables you to refine or coarsen your mesh based on the flow
solution.

You can read your mesh into Fluent or, for 3D geometries, create your mesh using
Fluent's meshing mode. All other operations are performed within Fluent's
solution mode, including:

- Setting boundary conditions
- Defining fluid properties
- Executing the solution
- Refining the mesh
- Running a parametric study 
- Postprocessing and viewing results

What is PyFluent?
-----------------
PyFluent is part of the `PyAnsys <https://docs.pyansys.com>`_ ecosystem that
lets you use Fluent within a Python environment of your choice in conjunction
with other PyAnsys libraries and external Python libraries.

PyFluent implements a client-server architecture. It uses Google remote
procedure calls, or gRPC interfaces, to launch or connect with a running Fluent
process as a server. However, you only need to interact with the Python
interface.

You can use PyFluent to programmatically create, interact with, and control a
Fluent session to create your own customized workspace. In addition, you can use
PyFluent to enhance your productivity with highly configurable, customized
scripts.

Features
--------
Some of the many features in this primary PyFluent package,
``ansys-fluent-core``, allow you to:

- Launch the Fluent solver in serial or parallel and connect to already-running
  Fluent sessions. For more information, see :ref:`ref_user_guide_launch`.
- Script using Fluent's meshing capabilities. For more information, see
  :ref:`ref_meshing`.
- Script using all of Fluent's TUI  (text user interface) commands. For more
  information, see :ref:`ref_user_guide_tui_commands`.
- Run more than one Fluent session asynchronously. For more information, see
  :ref:`ref_utils`.
- Retrieve Fluent field data as numpy arrays for custom postprocessing using
  standard Python packages such as `matplotlib <https://matplotlib.org/>`_. For
  more information, see :ref:`ref_field_data`.
- Register function callbacks on Fluent solver events such as when a case file
  or data file is read or when the Fluent solver completes an iteration. For
  more information, see :ref:`ref_events`.
- Retrieve solver monitors such as residuals. For more information, see
  :ref:`ref_monitors`.

Documentation and issues
------------------------
In addition to installation and usage information, the PyFluent documentation
provides :ref:`ref_index_api`, :ref:`ref_example_gallery`, and
:ref:`ref_contributing` sections.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

On the `PyFluent Issues <https://github.com/pyansys/pyfluent/issues>`_ page, you
can create issues to submit questions, report bugs, and request new features. To
reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

License
-------
PyFluent is licensed under the MIT license.

PyFluent makes no commercial claim over Ansys whatsoever. This library extends
the functionality of Ansys Fluent by adding a Python interface to Fluent without
changing the core behavior or license of the original software. The use of the
interactive control of Fluent control of PyFluent requires a legally licensed
copy of Fluent.

For more information on Fluent, see the `Ansys Fluent page
<https://www.ansys.com/products/fluids/ansys-fluent>`_ on the Ansys website.

Project index
-------------

* :ref:`genindex`
