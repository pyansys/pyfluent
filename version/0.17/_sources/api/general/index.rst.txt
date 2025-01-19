.. _ref_general:

General
=======

Launcher
########

:ref:`ref_launcher` includes instructions on how to launch and connect to Fluent.

Sessions
########

:ref:`ref_sessions` describes the various types of PyFluent session objects, which connect to Fluent sessions.

Services
########

:ref:`ref_services` outlines fundamental gRPC services, upon which PyFluent depends (and are directly usable).

Streaming services
##################

:ref:`ref_streaming_services` outlines fundamental gRPC streaming services, upon which PyFluent depends (and are directly usable).

Scheduler
#########

:ref:`ref_scheduler` describes a module for facilitating use of external job scheduling systems.

Case
####

:ref:`ref_case_reader` documents a class for parsing Fluent case files in pure Python code.

Data transfer
#############

:ref:`ref_data_transfer` describes how to transfer mesh data between PyFluent sessions.

Journaling
##########

:ref:`ref_journaling` explains how to read and write Python journals that are reusable between PyFluent and Fluent.

Workflow
########

:ref:`ref_workflow` documents high-level interfaces to the task-based workflows, including meshing workflow.

rpvars
######

:ref:`ref_rpvars` shows how you can access and modify live Fluent rpvars via PyFluent.

Quantity
########

:ref:`ref_quantity` reveals a powerful quantity class that exposes real values and units of API (and other) objects.

Post objects
############

:ref:`ref_post_objects` documents visualization objects for interfacing to Matplotlib and pyvista.

Asynchronous execution
######################

:ref:`ref_execution_utils` documents tools for asynchronous function execution.

Search
######

:ref:`ref_search` documents tools for searching Fluent settings or commands.

Meta
####

:ref:`ref_meta` consists of some metaclasses used in the PyFluent codebase.

Logging
#######
.. automodule:: ansys.fluent.core.logging
    :members:

.. currentmodule:: ansys.fluent.core

.. autosummary::
    :toctree: _autosummary

.. toctree::
    :maxdepth: 2
    :hidden:

    launcher/index
    execution_utils
    search
    sessions/index
    services/index
    streaming_services/index
    post_objects/index
    scheduler/index
    case_reader
    data_transfer
    journaling
    meta
    quantity
    rpvars
    workflow
