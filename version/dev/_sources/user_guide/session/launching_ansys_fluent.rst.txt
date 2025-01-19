.. _ref_launch_guide:

Launching and connecting to Fluent
==================================
You can use the :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`
function to start Fluent from Python. This code starts Fluent in the background and starts
Fluent's gRPC server so that commands can be sent to it from the Python interpreter:

.. code:: python

  >>> import ansys.fluent.core as pyfluent
  >>> solver = pyfluent.launch_fluent(
  >>>     mode=pyfluent.FluentMode.SOLVER
  >>> )


You can use the :func:`connect_to_fluent() <ansys.fluent.core.launcher.launcher.connect_to_fluent>`
function to connect to a running Fluent session that has already started the gRPC server. There are
some options for starting Fluent's gRPC server:

1. Start Fluent with ``<fluent_executable> -sifile=<server_info_file_name>``, or
2. Execute the ``server/start-server`` solution mode TUI command in Fluent, or
3. Execute ``File -> Applications -> Server -> Start...`` from the Fluent GUI ribbon menu in solution mode.

On starting the gRPC server, Fluent writes out a server-info file at ``<server_info_file_name>`` and
prints this information in the console. If you do not specify a particular ``<server_info_file_name>``,
it is automatically generated.

This code connects to a running Fluent session where the server-info file is server.txt in the working
directory:

.. code:: python

  >>> import ansys.fluent.core as pyfluent
  >>> solver = pyfluent.connect_to_fluent(
  >>>     server_info_file_name="server.txt"
  >>> )


Launcher options
----------------
The following examples show different ways that you can launch Fluent locally.
For more information, see :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.

Solver mode
~~~~~~~~~~~
These two examples show equivalent ways to launch Fluent in solution mode:

.. code:: python

  >>> solver = pyfluent.launch_fluent(
  >>>     mode=pyfluent.FluentMode.SOLVER
  >>> )
  

.. code:: python

  >>> solver = pyfluent.launch_fluent()


Meshing mode
~~~~~~~~~~~~
This example shows how to launch Fluent in meshing mode:

.. code:: python

  >>> meshing_session = pyfluent.launch_fluent(
  >>>      mode=pyfluent.FluentMode.MESHING
  >>> )


Precision
~~~~~~~~~
This example shows how to launch Fluent in solution mode
and set the floating point precision:

.. code:: python

  >>> solver = pyfluent.launch_fluent(
  >>>      precision=pyfluent.Precision.DOUBLE
  >>> )


Dimension
~~~~~~~~~
This example shows how to launch Fluent in solution mode and set the
modeling dimension to two:

.. code:: python

  >>> solver = pyfluent.launch_fluent(
  >>>      precision=pyfluent.Precision.DOUBLE,
  >>>      dimension=pyfluent.Dimension.TWO
  >>> )


Local parallel
~~~~~~~~~~~~~~
This example shows how to launch Fluent in solution mode and set the
number of processors for local parallel execution:

.. code:: python

  >>> solver = pyfluent.launch_fluent(
  >>>      precision=pyfluent.Precision.DOUBLE,
  >>>      dimension=pyfluent.Dimension.TWO,
  >>>      processor_count=2
  >>> )


Distributed parallel
~~~~~~~~~~~~~~~~~~~~
This example shows how to launch Fluent in solution mode with 16 processors
distributed across more than one machine:

.. code:: python

  >>> solver = pyfluent.launch_fluent(
  >>>     precision=pyfluent.Precision.DOUBLE,
  >>>     dimension=pyfluent.Dimension.THREE,
  >>>     processor_count=16
  >>>     additional_arguments="-cnf=m1:8,m2:8",
  >>> )


Logging support
---------------
PyFluent has an option to run with logging enabled.
This command enables logging:

.. code:: python

  >>> pyfluent.logging.enable()


For more details, see :ref:`ref_logging_guide`.

Scheduler support
-----------------
When PyFluent is used within a job scheduler environment, the :func:`launch_fluent()
<ansys.fluent.core.launcher.launcher.launch_fluent>` function automatically determines
the list of machines and core counts with which to start Fluent. The supported
scheduler environments are Altair Grid Engine (formerly UGE), Sun Grid Engine (SGE),
Load Sharing Facility (LSF), Portable Batch System (PBS), and Slurm.

This example shows a bash shell script that can be submitted to a Slurm
scheduler using the ``sbatch`` command:

.. code:: bash

   #!/bin/bash
   #SBATCH --job-name="pyfluent"
   #SBATCH --nodes=8
   #SBATCH --ntasks=32
   #SBATCH --output="%x_%j.log"
   #SBATCH --partition=mpi01
   #
   # Change to the directory where the Slurm job was submitted
   #
   cd $SLURM_SUBMIT_DIR
   #
   # Activate your favorite Python environment
   #
   export AWP_ROOT251=/apps/ansys_inc/v251
   . ./venv/bin/activate
   #
   # Run a PyFluent script
   #
   python run.py


Here are a few notes about this example:

- Eight machines with a total of 32 cores are requested. Fluent is started with
  the appropriate command line arguments passed to ``-t`` and ``-cnf``.
- The variable ``AWP_ROOT251`` is configured so that PyFluent can find
  the Fluent installation.
- The code assumes that a Python virtual environment was pre-configured with
  PyFluent installed before the job script is submitted to Slurm. You could
  also configure the virtual environment as part of the job script if desired.
- The ``run.py`` file can contain any number of PyFluent commands using any of
  the supported interfaces.

Within the scheduler environment, the
:func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`
function can be used in a few different ways. This example shows how to start
the three-dimensional, double precision version of Fluent on all the requested
machines and cores:

.. code:: python

  >>> solver = pyfluent.launch_fluent(
  >>>      precision=pyfluent.Precision.DOUBLE,
  >>>      dimension=pyfluent.Dimension.THREE
  >>> )


You can use the ``processor_count`` argument to set the number of cores that
Fluent uses:

.. code:: python

  >>> solver = pyfluent.launch_fluent(
  >>>     precision=pyfluent.Precision.DOUBLE,
  >>>     dimension=pyfluent.Dimension.THREE,
  >>>     processor_count=16,
  >>>     mode=pyfluent.FluentMode.SOLVER
  >>> )


Passing the ``processor_count`` parameter like this forces execution of Fluent on 16
cores, despite the fact that the Slurm submission requests 32 total cores from
the job scheduler. This behavior may be useful in situations where the scheduler
environment allocates all the cores on a machine and you know that Fluent may
not scale well on all the allocated cores.

Finally, if you want to ignore the scheduler allocation, you can pass either the ``-t``
argument or both the ``-t`` and ``-cnf`` arguments to the
:func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>` function
using the ``additional_arguments`` parameter. For local parallel execution, simply pass the
``-t`` argument:

.. code:: python

  >>> solver = pyfluent.launch_fluent(
  >>>     precision=pyfluent.Precision.DOUBLE,
  >>>     dimension=pyfluent.Dimension.THREE,
  >>>     additional_arguments="-t16"
  >>> )


For distributed parallel processing, you usually pass both parameters:

.. code:: python

  >>> solver = pyfluent.launch_fluent(
  >>>     precision=pyfluent.Precision.DOUBLE,
  >>>     dimension=pyfluent.Dimension.THREE,
  >>>     additional_arguments="-t16 -cnf=m1:8,m2:8",
  >>> )


The :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>` function
also supports the ``scheduler_options`` parameter to submit the Fluent job to a Slurm
scheduler without using any bash script:

.. code:: python

  >>> slurm = pyfluent.launch_fluent(
  >>>     scheduler_options={
  >>>         "scheduler": "slurm",
  >>>         "scheduler_headnode": "<headnode>",
  >>>         "scheduler_queue": "<queue>",
  >>>         "scheduler_account": "<account>"
  >>>     },
  >>>     additional_arguments="-t16 -cnf=m1:8,m2:8",
  >>> )
  >>> solver = slurm.result()


.. vale off

The keys ``scheduler_headnode``, ``scheduler_queue`` and ``scheduler_account`` are
optional and should be specified in a similar manner to Fluent's scheduler options.
Here, the :func:`launch_fluent <ansys.fluent.core.launcher.launcher.launch_fluent>`
function returns a :class:`SlurmFuture <ansys.fluent.core.launcher.slurm_launcher.SlurmFuture>`
instance from which the PyFluent session can be extracted. For a detailed usage, see the
documentation of the :mod:`slurm_launcher <ansys.fluent.core.launcher.slurm_launcher>`
module.

.. vale on

The ``scheduler_options`` parameter doesn't support the automatic scheduler allocation,
the ``-t`` and ``-cnf`` arguments must be passed to the
:func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>` function
using the ``additional_arguments`` parameter for distributed parallel processing.
