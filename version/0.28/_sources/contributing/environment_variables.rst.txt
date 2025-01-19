.. _ref_environment_variables:

=====================
Environment Variables
=====================

Following is a list of environment variables that can be set to control various aspects of PyFluent.

.. list-table::
    :header-rows: 1

    * - Variable
      - Description
    * - ANSYSLMD_LICENSE_FILE
      - Specifies the license server for Fluent.
    * - AWP_ROOT<NNN>
      - Specifies the Fluent root directory for the version vNNN while launching Fluent in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
    * - FLUENT_CONTAINER_IMAGE
      - Specifies the full Docker image name including tag while starting a Fluent container in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
    * - FLUENT_IMAGE_NAME
      - Specifies the Docker image name while starting a Fluent container in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
    * - FLUENT_IMAGE_TAG
      - Specifies the Docker image tag while starting a Fluent container in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
    * - PYFLUENT_CODEGEN_OUTDIR
      - Specifies the directory where API files are written out during codegen.
    * - PYFLUENT_CODEGEN_SKIP_BUILTIN_SETTINGS
      - Skips the generation of built-in settings during codegen.
    * - PYFLUENT_CONTAINER_MOUNT_SOURCE
      - Specifies the host path which is mounted inside the container while starting a Fluent container in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
    * - PYFLUENT_CONTAINER_MOUNT_TARGET
      - Specifies the path inside the container where the host path is mounted while starting a Fluent container in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
    * - PYFLUENT_FLUENT_DEBUG
      - Starts Fluent in debug mode while launching Fluent in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
    * - PYFLUENT_DOC_SKIP_CHEATSHEET:
      - Skips the generation of cheatsheet.
    * - PYFLUENT_DOC_SKIP_EXAMPLES
      - Skips the generation of examples documentation.
    * - PYFLUENT_FLUENT_IP
      - Specifies the IP address of the Fluent server in :func:`connect_to_fluent() <ansys.fluent.core.launcher.launcher.connect_to_fluent>`.
    * - PYFLUENT_FLUENT_PORT
      - Specifies the port of the Fluent server in :func:`connect_to_fluent() <ansys.fluent.core.launcher.launcher.connect_to_fluent>`.
    * - PYFLUENT_FLUENT_ROOT
      - Specifies the Fluent root directory while launching Fluent in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
    * - PYFLUENT_GRPC_LOG_BYTES_LIMIT
      - Specifies the length of gRPC logging messages. Set to 0 to disable the limit.
    * - PYFLUENT_LAUNCH_CONTAINER
      - Starts a Fluent container in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
    * - PYFLUENT_LOGGING
      - Enabled PyFluent logging and specifies the logging level. Possible values are ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, and ``CRITICAL``.
    * - PYFLUENT_NO_FIX_PARAMETER_LIST_RETURN
      - Disables the return value fix for the parameter list command in settings API.
    * - PYFLUENT_SHOW_SERVER_GUI
      - Shows the Fluent GUI while launching Fluent in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
    * - PYFLUENT_SKIP_API_UPGRADE_ADVICE
      - Disables printing of TUI to settings API upgrade advice.
    * - PYFLUENT_TIMEOUT_FORCE_EXIT
      - Enables force exit while exiting a Fluent session and specifies the timeout in seconds.
    * - PYFLUENT_WATCHDOG_DEBUG
      - Enables debugging for the PyFluent watchdog process.
    * - PYFLUENT_WATCHDOG_EXCEPTION_ON_ERROR
      - Raises exception when error occurs in the PyFluent watchdog process.
    * - REMOTING_PORTS
      - Specifies the port range for the Fluent server while launching Fluent in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
        The format is ``<start_port>/portspan=<port_span>``.
    * - REMOTING_SERVER_ADDRESS
      - Specifies the IP address of the Fluent server while launching Fluent in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
    * - SERVER_INFO_DIR
      - Specifies the directory where the server-info file is created while launching Fluent in :func:`launch_fluent() <ansys.fluent.core.launcher.launcher.launch_fluent>`.
