.. _ref_user_guide_launch:

Launch or connect to Fluent
===========================
You can use the :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`
method to start Fluent from Python in gRPC mode. This code starts Fluent in the background
so that commands can be sent to Fluent from the Python interpreter:

.. code:: python

    import ansys.fluent.core as pyfluent
    solver = pyfluent.launch_fluent(mode="solver")

You can use the :func:`connect_to_fluent() <ansys.fluent.core.launcher.launcher.connect_to_fluent>`
method to connect to a running Fluent session that has started the gRPC server. The gRPC
server in Fluent can be started using the ``-sifile=<server_info_filepath>`` command line
startup option, ``server/start-server`` text command or
``File -> Applications -> Server -> Start...`` ribbon menu. Fluent writes out a server-info file on
starting the gRPC server. This code connects to a running Fluent session
using a server-info file server.txt in the working directory:

.. code:: python

    import ansys.fluent.core as pyfluent
    solver = pyfluent.connect_to_fluent(server_info_filepath="server.txt")

Launcher options
----------------
The following examples show different ways that you can launch Fluent locally.
For more information, see :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.

Solver mode
~~~~~~~~~~~
This example shows how to launch Fluent in solution mode:

.. code:: python

   solver = pyfluent.launch_fluent(mode="solver")

Meshing mode
~~~~~~~~~~~~
This example shows how to launch Fluent in meshing mode:

.. code:: python

   meshing_session = pyfluent.launch_fluent(mode="meshing")

Precision
~~~~~~~~~
This example shows how to launch Fluent in solution mode
and set the floating point precision:

.. code:: python

   solver = pyfluent.launch_fluent(precision="double", mode="solver")

Dimension
~~~~~~~~~
This example shows how to launch Fluent in solution mode and set the
modeling dimension:

.. code:: python

   solver = pyfluent.launch_fluent(precision="double", version="2d", mode="solver")

Local parallel
~~~~~~~~~~~~~~
This example shows how to launch Fluent in solution mode and set the
number of processors for local parallel execution:

.. code:: python

   solver = pyfluent.launch_fluent(
      precision="double", version="2d", processor_count=2, mode="solver"
   )

Distributed parallel
~~~~~~~~~~~~~~~~~~~~
This example shows how to launch Fluent in solution mode with 16 processors
distributed across more than one machine:

.. code:: python

   solver = pyfluent.launch_fluent(
      precision="double",
      version="3d",
      processor_count=16,
      mode="solver",
      additional_arguments="-cnf=m1:8,m2:8",
   )

Logging support
---------------
PyFluent has an option to run with logging enabled.
This command enables logging:

.. code:: python

   pyfluent.set_log_level("ERROR")

When enabling logging, you must pass the log level. PyFluent supports any of the
Python logging levels (``"CRITICAL"``, ``"ERROR"``, ``"WARNING"``, ``"INFO"``, and ``"DEBUG"``)
in string or ``enum`` format.

Scheduler support
-----------------
When PyFluent is run within a job scheduler environment, the :func:`launch_fluent()
<ansys.fluent.core.launcher.launcher.launch_fluent>` method automatically determines
the list of machines and core counts to start Fluent with. The supported
scheduler environments are Univa Grid Engine (UGE), Load Sharing Facility (LSF),
Portable Batch System (PBS), and Slurm.

This example shows a bash shell script that can be submitted to a Slurm
scheduler using the ```sbatch``` command:  

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
   export AWP_ROOT232=/apps/ansys_inc/v232
   . ./venv/bin/activate
   #
   # Run a PyFluent script
   #
   python run.py

Here are a few notes about this example:

- Eight machines with a total of 32 cores are requested. Fluent is started with
  the appropriate command line arguments passed to ``-t`` and ``-cnf``.
- The variable ``AWP_ROOT232`` is configured so that PyFluent knows where to find
  the Fluent installation.
- The code assumes that a Python virtual environment was pre-configured with
  PyFluent installed before the job script is submitted to Slurm. You could
  also configure the virtual environment as part of the job script if desired.
- The ``run.py`` file can contain any number of PyFluent commands using any of
  the supported interfaces.

Once running within the scheduler environment, the
:func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`
method can be used in a few different ways. This example shows how to start
the three-dimensional, double precision version of Fluent on all the requested
machines and cores:

.. code:: python

   solver = pyfluent.launch_fluent(precision="double", version="3d", mode="solver")

If you want to clamp the number of cores that Fluent is launched on, you can
pass the ``processor_count`` parameter:

.. code:: python

   solver = pyfluent.launch_fluent(
      precision="double", version="3d", processor_count=16, mode="solver"
   )

Passing the ``processor_count`` parameter like this forces execution of Fluent on 16
cores, despite the fact that the Slurm submission requests 32 total cores from
the job scheduler. This behavior may be useful in situations where the scheduler
environment allocates all the cores on a machine and you know that Fluent may
not scale well on all the allocated cores.

Finally, if you want to ignore the scheduler allocation, you can pass the ``-t``
or ``-t`` and ``-cnf`` arguments to the
:func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>` method
using the ``additional_arguments`` parameter. For local parallel execution, simply pass the ``-t``
argument:

.. code:: python

   solver = pyfluent.launch_fluent(
      precision="double", version="3d", mode="solver", additional_arguments="-t16"
   )

For distributed parallel processing, you usually pass both parameters:

.. code:: python

   solver = pyfluent.launch_fluent(
      precision="double",
      version="3d",
      mode="solver",
      additional_arguments="-t16 -cnf=m1:8,m2:8",
   )