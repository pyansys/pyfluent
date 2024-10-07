"""Provides a module for launching Fluent.

This module supports both starting Fluent locally and connecting to a remote instance
with gRPC.
"""

import inspect
import logging
import os
from pathlib import Path
from typing import Any, Dict

import ansys.fluent.core as pyfluent
from ansys.fluent.core.fluent_connection import FluentConnection
from ansys.fluent.core.launcher.container_launcher import DockerLauncher
from ansys.fluent.core.launcher.launcher_utils import _confirm_watchdog_start
from ansys.fluent.core.launcher.pim_launcher import PIMLauncher
from ansys.fluent.core.launcher.pyfluent_enums import (
    Dimension,
    FluentLinuxGraphicsDriver,
    FluentMode,
    FluentWindowsGraphicsDriver,
    LaunchMode,
    Precision,
    UIMode,
    _get_fluent_launch_mode,
    _get_running_session_mode,
)
from ansys.fluent.core.launcher.server_info import _get_server_info
from ansys.fluent.core.launcher.slurm_launcher import SlurmFuture, SlurmLauncher
from ansys.fluent.core.launcher.standalone_launcher import StandaloneLauncher
import ansys.fluent.core.launcher.watchdog as watchdog
from ansys.fluent.core.session_meshing import Meshing
from ansys.fluent.core.session_pure_meshing import PureMeshing
from ansys.fluent.core.session_solver import Solver
from ansys.fluent.core.session_solver_icing import SolverIcing
from ansys.fluent.core.utils.deprecate import deprecate_argument
from ansys.fluent.core.utils.fluent_version import FluentVersion
from ansys.fluent.core.warnings import PyFluentDeprecationWarning

_THIS_DIR = os.path.dirname(__file__)
_OPTIONS_FILE = os.path.join(_THIS_DIR, "fluent_launcher_options.json")
logger = logging.getLogger("pyfluent.launcher")


def create_launcher(fluent_launch_mode: LaunchMode = None, **kwargs):
    """Use the factory function to create a launcher for supported launch modes.

    Parameters
    ----------
    fluent_launch_mode: LaunchMode
        Supported Fluent launch modes. Options are ``"LaunchMode.CONTAINER"``,
        ``"LaunchMode.PIM"``, ``"LaunchMode.SLURM"``, and ``"LaunchMode.STANDALONE"``.
    kwargs : Any
        Keyword arguments.
    Returns
    -------
    launcher: DockerLauncher | PimLauncher | StandaloneLauncher
        Session launcher.
    Raises
    ------
    DisallowedValuesError
        If an unknown Fluent launch mode is passed.
    """
    if fluent_launch_mode == LaunchMode.STANDALONE:
        return StandaloneLauncher(**kwargs)
    elif fluent_launch_mode == LaunchMode.CONTAINER:
        return DockerLauncher(**kwargs)
    elif fluent_launch_mode == LaunchMode.PIM:
        return PIMLauncher(**kwargs)
    elif fluent_launch_mode == LaunchMode.SLURM:
        return SlurmLauncher(**kwargs)


def _version_to_dimension(old_arg_val):
    if old_arg_val == "2d":
        return Dimension.TWO
    elif old_arg_val == "3d":
        return Dimension.THREE
    else:
        return None


#   pylint: disable=unused-argument
@deprecate_argument(
    old_arg="show_gui",
    new_arg="ui_mode",
    converter=lambda old_arg_val: UIMode.GUI if old_arg_val is True else None,
    warning_cls=PyFluentDeprecationWarning,
)
@deprecate_argument(
    old_arg="version",
    new_arg="dimension",
    converter=_version_to_dimension,
    warning_cls=PyFluentDeprecationWarning,
)
def launch_fluent(
    product_version: FluentVersion | str | float | int | None = None,
    dimension: Dimension | int | None = None,
    precision: Precision | str | None = None,
    processor_count: int | None = None,
    journal_file_names: None | str | list[str] = None,
    start_timeout: int = None,
    additional_arguments: str | None = "",
    env: Dict[str, Any] | Path | None = None,
    start_container: bool | None = None,
    container_dict: dict | None = None,
    dry_run: bool = False,
    cleanup_on_exit: bool = True,
    start_transcript: bool = True,
    ui_mode: UIMode | str | None = None,
    graphics_driver: (
        FluentWindowsGraphicsDriver | FluentLinuxGraphicsDriver | str | None
    ) = None,
    case_file_name: str | None = None,
    case_data_file_name: str | None = None,
    lightweight_mode: bool | None = None,
    mode: FluentMode | str | None = None,
    py: bool | None = None,
    gpu: bool | list[int] | None = None,
    cwd: str | None = None,
    fluent_path: str | None = None,
    topy: str | list | None = None,
    start_watchdog: bool | None = None,
    scheduler_options: dict | None = None,
    file_transfer_service: Any | None = None,
    enable_data_model_api_upgrades: bool | None = None,
) -> Meshing | PureMeshing | Solver | SolverIcing | SlurmFuture | dict:
    """Launch Fluent locally in server mode or connect to a running Fluent server
    instance.

    Parameters
    ----------
    product_version : FluentVersion or str or float or int, optional
        Version of Ansys Fluent to launch. To use Fluent version 2024 R2, pass
        any of  ``FluentVersion.v242``, ``"24.2.0"``, ``"24.2"``, ``24.2``or ``242``.
        The default is ``None``, in which case the newest installed version is used.
    dimension : Dimension or int, optional
        Geometric dimensionality of the Fluent simulation. The default is ``None``,
        in which case ``Dimension.THREE`` is used. Options are either the values of the
        ``Dimension`` enum (``Dimension.TWO`` or ``Dimension.THREE``) or any of ``2`` and ``3``.
    precision : Precision or str, optional
        Floating point precision. The default is ``None``, in which case ``Precision.DOUBLE``
        is used. Options are either the values of the ``Precision`` enum (``Precision.SINGLE``
        or ``Precision.DOUBLE``) or any of ``"double"`` and ``"single"``.
    processor_count : int, optional
        Number of processors. The default is ``None``, in which case ``1``
        processor is used.  In job scheduler environments the total number of
        allocated cores is clamped to value of ``processor_count``.
    journal_file_names : str or list of str, optional
        The string path to a Fluent journal file, or a list of such paths. Fluent will execute the
        journal(s). The default is ``None``.
    start_timeout : int, optional
        Maximum allowable time in seconds for connecting to the Fluent
        server. The default is ``60`` if Fluent is launched outside a Slurm environment,
        no timeout if Fluent is launched within a Slurm environment.
    additional_arguments : str, optional
        Additional arguments to send to Fluent as a string in the same
        format they are normally passed to Fluent on the command line.
    env : dict[str, str], optional
        Mapping to modify environment variables in Fluent. The default
        is ``None``.
    start_container : bool, optional
        Specifies whether to launch a Fluent Docker container image. For more details about containers, see
        :mod:`~ansys.fluent.core.launcher.fluent_container`.
    container_dict : dict, optional
        Dictionary for Fluent Docker container configuration. If specified,
        setting ``start_container = True`` as well is redundant.
        Will launch Fluent inside a Docker container using the configuration changes specified.
        See also :mod:`~ansys.fluent.core.launcher.fluent_container`.
    dry_run : bool, optional
        Defaults to False. If True, will not launch Fluent, and will instead print configuration information
        that would be used as if Fluent was being launched. If dry running a container start,
        ``launch_fluent()`` will return the configured ``container_dict``.
    cleanup_on_exit : bool, optional
        Whether to shut down the connected Fluent session when PyFluent is
        exited, or the ``exit()`` method is called on the session instance,
        or if the session instance becomes unreferenced. The default is ``True``.
    start_transcript : bool, optional
        Whether to start streaming the Fluent transcript in the client. The
        default is ``True``. You can stop and start the streaming of the
        Fluent transcript subsequently via the method calls, ``transcript.start()``
        and ``transcript.stop()`` on the session object.
    ui_mode : UIMode or str, optional
        Fluent user interface mode. Options are either the values of the ``UIMode``
        enum or any of ``"no_gui_or_graphics"``, ``"no_gui"``, ``"hidden_gui"``,
        ``"no_graphics"`` or ``"gui"``. The default is ``UIMode.HIDDEN_GUI`` in
        Windows and ``UIMode.NO_GUI`` in Linux. ``"no_gui_or_graphics"`` and
        ``"no_gui"`` user interface modes are supported in Windows starting from Fluent
        version 2024 R1.
    graphics_driver : FluentWindowsGraphicsDriver or FluentLinuxGraphicsDriver or str, optional
        Graphics driver of Fluent. In Windows, options are either the values of the
        ``FluentWindowsGraphicsDriver`` enum or any of ``"null"``, ``"msw"``,
        ``"dx11"``, ``"opengl2"``, ``"opengl"`` or ``"auto"``. In Linux, options are
        either the values of the ``FluentLinuxGraphicsDriver`` enum or any of
       ``"null"``, ``"x11"``, ``"opengl2"``, ``"opengl"`` or ``"auto"``. The default is
       ``FluentWindowsGraphicsDriver.AUTO`` in Windows and
       ``FluentLinuxGraphicsDriver.AUTO`` in Linux.
    case_file_name : str, optional
        If provided, the case file at ``case_file_name`` is read into the Fluent session.
    case_data_file_name : str, optional
        If provided, the case and data files at ``case_data_file_name`` are read into the Fluent session.
    lightweight_mode : bool, optional
        Whether to run in lightweight mode. In lightweight mode, the lightweight settings are read into the
        current Fluent solver session. The mesh is read into a background Fluent solver session which will
        replace the current Fluent solver session once the mesh read is complete and the lightweight settings
        made by the user in the current Fluent solver session have been applied in the background Fluent
        solver session. This is all orchestrated by PyFluent and requires no special usage.
        This parameter is used only when ``case_file_name`` is provided. The default is ``False``.
    mode : str, optional
        Launch mode of Fluent to point to a specific session type.
        The default value is ``None``. Options are ``"meshing"``,
        ``"pure-meshing"`` and ``"solver"``.
    py : bool, optional
        If True, Fluent will run in Python mode. Default is None.
    gpu : bool or list, optional
        This option will start Fluent with the GPU Solver. A list of GPU IDs can be
        passed to use specific GPUs. If True is passed, the number of GPUs used will be
        clamped to the value of ``processor_count``. Please refer to
        *Starting the Fluent GPU Solver* section in *Fluent's User Guide* for more
        information like how to determine the GPU IDs.
    cwd : str, Optional
        Working directory for the Fluent client.
    fluent_path: str, Optional
        User provided Fluent installation path.
    topy : bool or str, optional
        A boolean flag to write the equivalent Python journal(s) from the journal(s) passed.
        Can optionally take the file name of the new python journal file.
    start_watchdog : bool, optional
        When ``cleanup_on_exit`` is True, ``start_watchdog`` defaults to True,
        which means an independent watchdog process is run to ensure
        that any local GUI-less Fluent sessions started by PyFluent are properly closed (or killed if frozen)
        when the current Python process ends.
    scheduler_options : dict, optional
        Dictionary containing scheduler options. Default is None.

        Currently only the Slurm scheduler is supported. The ``scheduler_options``
        dictionary must be of the form ``{"scheduler": "slurm",
        "scheduler_headnode": "<headnode>", "scheduler_queue": "<queue>",
        "scheduler_account": "<account>"}``. The keys ``scheduler_headnode``,
        ``scheduler_queue`` and ``scheduler_account`` are optional and should be
        specified in a similar manner to Fluent's scheduler options.
    file_transfer_service : optional
        File transfer service. Uploads/downloads files to/from the server.
    enable_data_model_api_upgrades : bool, optional
        This option enables experimental code in Fluent, which provides further
        improvements to the enhanced meshing workflow API.
    Returns
    -------
    :obj:`~typing.Union` [:class:`Meshing<ansys.fluent.core.session_meshing.Meshing>`, \
    :class:`~ansys.fluent.core.session_pure_meshing.PureMeshing`, \
    :class:`~ansys.fluent.core.session_solver.Solver`, \
    :class:`~ansys.fluent.core.session_solver_icing.SolverIcing`, dict]
        Session object or configuration dictionary if ``dry_run = True``.

    Raises
    ------
    UnexpectedKeywordArgument
        If an unexpected keyword argument is provided.

    Notes
    -----
    Job scheduler environments such as SLURM, LSF, PBS, etc. allocates resources / compute nodes.
    The allocated machines and core counts are queried from the scheduler environment and
    passed to Fluent.
    """
    if env is None:
        env = {}

    def _mode_to_launcher_type(fluent_launch_mode: LaunchMode):
        launcher_mode_type = {
            LaunchMode.CONTAINER: DockerLauncher,
            LaunchMode.PIM: PIMLauncher,
            LaunchMode.SLURM: SlurmLauncher,
            LaunchMode.STANDALONE: StandaloneLauncher,
        }
        return launcher_mode_type[fluent_launch_mode]

    argvals = inspect.getargvalues(inspect.currentframe()).locals

    fluent_launch_mode = _get_fluent_launch_mode(
        start_container=start_container,
        container_dict=container_dict,
        scheduler_options=scheduler_options,
    )

    launcher_type = _mode_to_launcher_type(fluent_launch_mode)
    launch_fluent_args = set(inspect.signature(launch_fluent).parameters.keys())
    launcher_type_args = set(
        inspect.signature(launcher_type.__init__).parameters.keys()
    )
    common_args = launch_fluent_args.intersection(launcher_type_args)
    launcher_argvals = {arg: val for arg, val in argvals.items() if arg in common_args}
    if pyfluent.START_WATCHDOG is False:
        launcher_argvals["start_watchdog"] = False
    launcher = launcher_type(**launcher_argvals)
    return launcher()


def connect_to_fluent(
    ip: str | None = None,
    port: int | None = None,
    cleanup_on_exit: bool = False,
    start_transcript: bool = True,
    server_info_file_name: str | None = None,
    password: str | None = None,
    start_watchdog: bool | None = None,
) -> Meshing | PureMeshing | Solver | SolverIcing:
    """Connect to an existing Fluent server instance.

    Parameters
    ----------
    ip : str, optional
        IP address for connecting to an existing Fluent instance. The
        IP address defaults to ``"127.0.0.1"``. You can also use the environment
        variable ``PYFLUENT_FLUENT_IP=<ip>`` to set this parameter.
        The explicit value of ``ip`` takes precedence over ``PYFLUENT_FLUENT_IP=<ip>``.
    port : int, optional
        Port to listen on for an existing Fluent instance. You can use the
        environment variable ``PYFLUENT_FLUENT_PORT=<port>`` to set a default
        value. The explicit value of ``port`` takes precedence over
        ``PYFLUENT_FLUENT_PORT=<port>``.
    cleanup_on_exit : bool, optional
        Whether to shut down the connected Fluent session when PyFluent is
        exited, or the ``exit()`` method is called on the session instance,
        or if the session instance becomes unreferenced. The default is ``False``.
    start_transcript : bool, optional
        Whether to start streaming the Fluent transcript in the client. The
        default is ``True``. You can stop and start the streaming of the
        Fluent transcript subsequently via the method calls, ``transcript.start()``
        and ``transcript.stop()`` on the session object.
    server_info_file_name: str
        Path to server-info file written out by Fluent server. The default is
        ``None``. PyFluent uses the connection information in the file to
        connect to a running Fluent session.
    password : str, optional
        Password to connect to existing Fluent instance.
    start_watchdog: bool, optional
        When ``cleanup_on_exit`` is True, ``start_watchdog`` defaults to True,
        which means an independent watchdog process is run to ensure
        that any local Fluent connections are properly closed (or terminated if frozen) when Python process ends.

    Returns
    -------
    :obj:`~typing.Union` [:class:`Meshing<ansys.fluent.core.session_meshing.Meshing>`, \
    :class:`~ansys.fluent.core.session_pure_meshing.PureMeshing`, \
    :class:`~ansys.fluent.core.session_solver.Solver`, \
    :class:`~ansys.fluent.core.session_solver_icing.SolverIcing`]
        Session object.
    """
    ip, port, password = _get_server_info(server_info_file_name, ip, port, password)
    fluent_connection = FluentConnection(
        ip=ip,
        port=port,
        password=password,
        cleanup_on_exit=cleanup_on_exit,
    )
    new_session = _get_running_session_mode(fluent_connection)

    start_watchdog = _confirm_watchdog_start(
        start_watchdog, cleanup_on_exit, fluent_connection
    )

    if start_watchdog:
        logger.info("Launching Watchdog for existing Fluent session...")
        ip, port, password = _get_server_info(server_info_file_name, ip, port, password)
        watchdog.launch(os.getpid(), port, password, ip)

    return new_session(
        fluent_connection=fluent_connection,
        scheme_eval=fluent_connection._connection_interface.scheme_eval,
        start_transcript=start_transcript,
    )
