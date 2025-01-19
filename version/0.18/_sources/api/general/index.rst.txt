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

Data
####

:ref:`ref_data_reader` documents a class for parsing Fluent data files in pure Python code.

File session
############

:ref:`ref_file_session` expose field info and data for Fluent case and data files.

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

Post objects
############

:ref:`ref_post_objects` documents visualization objects for interfacing to Matplotlib and pyvista.

Execution utilities
###################

:ref:`ref_execution_utils` documents execution utilities, including an asynchronous option, for command execution.

Search
######

:ref:`ref_search` documents tools for searching Fluent settings or commands.

Meta
####

:ref:`ref_meta` consists of some metaclasses used in the PyFluent codebase.

Logging
#######

:ref:`ref_logging` documents the PyFluent debug logging module.

.. currentmodule:: ansys.fluent.core

.. autosummary::
    :toctree: _autosummary

.. toctree::
    :maxdepth: 2
    :hidden:

    launcher/index
    sessions/index
    services/index
    streaming_services/index
    scheduler/index
    fielddata
    fieldinfo
    case_reader
    data_transfer
    journaling
    workflow
    rpvars
    post_objects/index
    execution_utils
    search
    meta
    logging
