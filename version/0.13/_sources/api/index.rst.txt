API reference
=============

This section describes the core Pythonic interfaces for Fluent. Here, you can find the application programming
interfaces for such things as launching Fluent, assorted utilities, as well as the interfaces for the meshing and
solver components of Fluent.

General
#######

Features of PyFluent not specifically belonging to either the Meshing or Solver modes are collected together in the
:ref:`ref_general` section. That includes instructions on how to launch and connect to Fluent, and the various types of
PyFluent session objects, which connect to Fluent sessions, are documented. Fundamental gRPC services, including
streaming services, upon which PyFluent depends (and are directly usable) are outlined. Other features include a
Scheduler module for facilitating use of external job scheduling systems, a purely Python-based reader for Fluent
project and case files, Python-based journaling, task-based workflow objects, full Pythonic access to Fluent rp-vars,
powerful quantity objects that expose real values and units of API (and other) objects, visualization objects for
interfacing to Matplotlib and pyvista, and tools for asynchronous and batched command execution.

Meshing
#######

The :ref:`ref_meshing` mode provides Pythonic interfaces to the Fluent meshing TUI, Fluent meshing guided workflows,
and part management.

Solver
######

The :ref:`ref_solver` mode is dedicated to capturing the power of the Fluent solver. This component consists of a
:ref:`ref_settings`-based interface and a :ref:`ref_solver_tui`-based interface that is derived from the Fluent
Solver TUI, as well as access to surface data and scalar and vector field data.


.. toctree::
    :maxdepth: 2
    :hidden:

    general/index
    meshing/index
    solver/index
