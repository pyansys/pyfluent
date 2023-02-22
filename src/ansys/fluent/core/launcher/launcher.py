"""Provides a module for launching Fluent.

This module supports both starting Fluent locally and connecting to a
remote instance with gRPC.
"""
from enum import Enum
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile
import time
from typing import Any, Dict, Union
import warnings

from ansys.fluent.core.fluent_connection import _FluentConnection
from ansys.fluent.core.launcher.fluent_container import start_fluent_container
from ansys.fluent.core.scheduler import build_parallel_options, load_machines
from ansys.fluent.core.session import _BaseSession, parse_server_info_file
from ansys.fluent.core.session_meshing import Meshing
from ansys.fluent.core.session_pure_meshing import PureMeshing
from ansys.fluent.core.session_solver import Solver
from ansys.fluent.core.session_solver_icing import SolverIcing
from ansys.fluent.core.utils.logging import LOG
from ansys.fluent.core.utils.networking import find_remoting_ip
import ansys.platform.instancemanagement as pypim

_THIS_DIR = os.path.dirname(__file__)
_OPTIONS_FILE = os.path.join(_THIS_DIR, "fluent_launcher_options.json")


def _is_windows():
    """Check if the current operating system is windows."""
    return platform.system() == "Windows"


class FluentVersion(Enum):
    """Contains the standard Ansys Fluent release."""

    version_23R2 = "23.2.0"
    version_23R1 = "23.1.0"
    version_22R2 = "22.2.0"

    @classmethod
    def _missing_(cls, version):
        if isinstance(version, (float, str)):
            version = str(version) + ".0"
            for v in FluentVersion:
                if version == v.value:
                    return FluentVersion(version)
            else:
                raise RuntimeError(
                    f"The passed version '{version[:-2]}' does not exist."
                    f" Available version strings are: "
                    f"{[ver.value for ver in FluentVersion]} "
                )

    def __str__(self):
        return str(self.value)


def get_ansys_version() -> str:
    """Get the latest ANSYS version from AWP_ROOT environment variables."""
    for v in FluentVersion:
        if "AWP_ROOT" + "".join(str(v).split("."))[:-1] in os.environ:
            return str(v)

    raise RuntimeError("No ANSYS version can be found.")


def get_fluent_exe_path(**launch_argvals) -> Path:
    def get_fluent_root(version: FluentVersion) -> Path:
        awp_root = os.environ["AWP_ROOT" + "".join(str(version).split("."))[:-1]]
        return Path(awp_root) / "fluent"

    def get_exe_path(fluent_root: Path) -> Path:
        if _is_windows():
            return fluent_root / "ntbin" / "win64" / "fluent.exe"
        else:
            return fluent_root / "bin" / "fluent"

    # Look for Fluent exe path in the following order:
    # 1. "PYFLUENT_FLUENT_ROOT" environment variable
    fluent_root = os.getenv("PYFLUENT_FLUENT_ROOT")
    if fluent_root:
        return get_exe_path(Path(fluent_root))

    # 2. product_version parameter passed with launch_fluent
    product_version = launch_argvals.get("product_version")
    if product_version:
        return get_exe_path(get_fluent_root(FluentVersion(product_version)))

    # 3. the latest ANSYS version from AWP_ROOT environment variables
    ansys_version = get_ansys_version()
    return get_exe_path(get_fluent_root(FluentVersion(ansys_version)))


class LaunchModes(Enum):
    """Provides the standard Fluent launch modes."""

    # Tuple:   Name, Solver object type, Meshing flag, Launcher options
    MESHING_MODE = ("meshing", Meshing, True, [])
    PURE_MESHING_MODE = ("pure-meshing", PureMeshing, True, [])
    SOLVER = ("solver", Solver, False, [])
    SOLVER_ICING = ("solver-icing", SolverIcing, False, [("fluent_icing", True)])

    @staticmethod
    def get_mode(mode: str) -> "LaunchModes":
        """Returns the LaunchMode based on the mode in string format."""
        for m in LaunchModes:
            if mode == m.value[0]:
                return m
        else:
            raise RuntimeError(
                f"The passed mode '{mode}' matches none of the allowed modes."
            )


def _get_server_info_filepath():
    server_info_dir = os.getenv("SERVER_INFO_DIR")
    dir_ = Path(server_info_dir) if server_info_dir else tempfile.gettempdir()
    fd, filepath = tempfile.mkstemp(suffix=".txt", prefix="serverinfo-", dir=str(dir_))
    os.close(fd)
    return filepath


def _get_subprocess_kwargs_for_fluent(env: Dict[str, Any]) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    kwargs.update(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if _is_windows():
        kwargs.update(creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        kwargs.update(shell=True, start_new_session=True)
    fluent_env = os.environ.copy()
    fluent_env.update({k: str(v) for k, v in env.items()})
    fluent_env["REMOTING_THROW_LAST_TUI_ERROR"] = "1"
    from ansys.fluent.core import INFER_REMOTING_IP

    if INFER_REMOTING_IP:
        remoting_ip = find_remoting_ip()
        if remoting_ip:
            fluent_env["REMOTING_SERVER_ADDRESS"] = remoting_ip
    kwargs.update(env=fluent_env)
    return kwargs


def _build_fluent_launch_args_string(**kwargs) -> str:
    """Build Fluent's launch arguments string from keyword arguments.

    Returns
    -------
    str
        Fluent's launch arguments string.
    """
    all_options = None
    with open(_OPTIONS_FILE, encoding="utf-8") as fp:
        all_options = json.load(fp)
    launch_args_string = ""
    for k, v in all_options.items():
        argval = kwargs.get(k)
        default = v.get("default")
        if argval is None and v.get("fluent_required") is True:
            argval = default
        if argval is not None:
            allowed_values = v.get("allowed_values")
            if allowed_values and argval not in allowed_values:
                if default is not None:
                    old_argval = argval
                    argval = default
                    LOG.warning(
                        "Default value %s is chosen for %s as the passed "
                        "value  %s is outside allowed values %s.",
                        argval,
                        k,
                        old_argval,
                        allowed_values,
                    )
                else:
                    LOG.warning(
                        "%s = %s is discarded as it is outside " "allowed values %s.",
                        k,
                        argval,
                        allowed_values,
                    )
                    continue
            fluent_map = v.get("fluent_map")
            if fluent_map:
                if isinstance(argval, str):
                    json_key = argval
                else:
                    json_key = json.dumps(argval)
                argval = fluent_map[json_key]
            launch_args_string += v["fluent_format"].replace("{}", str(argval))
    addArgs = kwargs["additional_arguments"]
    if "-t" not in addArgs and "-cnf=" not in addArgs:
        mlist = load_machines(ncores=kwargs["processor_count"])
        launch_args_string += " " + build_parallel_options(mlist)
    return launch_args_string


def launch_remote_fluent(
    session_cls,
    start_transcript: bool,
    start_timeout: int = 100,
    product_version: str = None,
    cleanup_on_exit: bool = True,
    meshing_mode: bool = False,
    dimensionality: str = None,
    launcher_args: Dict[str, Any] = None,
):
    """Launch Fluent remotely using the PIM (Product Instance Management) API.

    When calling this method, you must ensure that you are in an
    environment where PyPIM is configured. You can use the :func:
    `pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to verify that PYPIM is configured.

    Parameters
    ----------
    session_cls: _BaseSession
        Instance of the Session class
    start_transcript: bool
        Whether to start streaming the Fluent transcript in the client. The
        default is ``True``. You can stop and start the streaming of the
        Fluent transcript subsequently via method calls on the session object.
    start_timeout : int, optional
        Maximum allowable time in seconds for connecting to the Fluent
        server. The default is ``100``.
    product_version : str, optional
        Version of Fluent to use in the three-digit format (such as ``"212"``
        for 2021 R2). The default is ``None``, in which case the active version
        or latest installed version is used.
    cleanup_on_exit : bool, optional
        Whether to clean up and exit Fluent when Python exits or when garbage
        is collected for the Fluent Python instance. The default is ``True``.
    meshing_mode : bool, optional
        Whether to launch Fluent remotely in meshing mode. The default is
        ``False``.
    dimensionality : str, optional
        Number of dimensions for modeling. The default is ``None``, in which
        case ``"3s"`` is used. Options are ``"3d"`` and ``"2d"``.

    Returns
    -------
    ansys.fluent.core.session.Session
        Instance of the session.
    """
    pim = pypim.connect()
    instance = pim.create_instance(
        product_name="fluent-meshing"
        if meshing_mode
        else "fluent-2ddp"
        if dimensionality == "2d"
        else "fluent-3ddp",
        product_version=product_version,
    )
    instance.wait_for_ready()
    # nb pymapdl sets max msg len here:
    channel = instance.build_grpc_channel()
    return session_cls(
        fluent_connection=_FluentConnection(
            channel=channel,
            cleanup_on_exit=cleanup_on_exit,
            remote_instance=instance,
            start_timeout=start_timeout,
            start_transcript=start_transcript,
            launcher_args=launcher_args,
        )
    )


def _get_session_info(argvals, mode: Union[LaunchModes, str, None] = None):
    """Updates the session information."""
    if mode is None:
        mode = LaunchModes.SOLVER

    if isinstance(mode, str):
        mode = LaunchModes.get_mode(mode)
    new_session = mode.value[1]
    meshing_mode = mode.value[2]
    for k, v in mode.value[3]:
        argvals[k] = v

    return new_session, meshing_mode, argvals, mode


def _raise_exception_g_gu_in_windows_os(additional_arguments: str) -> None:
    """If -g or -gu is passed in Windows OS, the exception should be raised."""
    if _is_windows() and (
        ("-g" in additional_arguments) or ("-gu" in additional_arguments)
    ):
        raise ValueError("'-g' and '-gu' is not supported on windows platform.")


def _update_launch_string_wrt_gui_options(
    launch_string: str, show_gui: bool = None, additional_arguments: str = ""
) -> str:
    """Checks for all gui options in additional arguments and updates the
    launch string with hidden, if none of the options are met."""

    if (show_gui is False) or (
        show_gui is None and (os.getenv("PYFLUENT_SHOW_SERVER_GUI") != "1")
    ):
        if not {"-g", "-gu"} & set(additional_arguments.split()):
            launch_string += " -hidden"

    return launch_string


def _await_fluent_launch(
    server_info_filepath: str, start_timeout: int, sifile_last_mtime: float
):
    """Wait for successful fluent launch or raise an error."""
    while True:
        if Path(server_info_filepath).stat().st_mtime > sifile_last_mtime:
            time.sleep(1)
            LOG.info("Fluent process is successfully launched.")
            break
        if start_timeout == 0:
            raise RuntimeError("The launch process has been timed out.")
        time.sleep(1)
        start_timeout -= 1
        LOG.info(
            "Waiting for Fluent to launch...%02d seconds remaining",
            start_timeout,
        )


def _connect_to_running_server(argvals, server_info_filepath: str):
    """Connect to an already running session."""
    ip = argvals.get("ip", None)
    port = argvals.get("port", None)
    password = argvals.get("password", None)
    if ip and port:
        warnings.warn(
            "The server-info file was not parsed because ip and port were provided explicitly."
        )
    elif server_info_filepath:
        ip, port, password = parse_server_info_file(server_info_filepath)
    elif os.getenv("PYFLUENT_FLUENT_IP") and os.getenv("PYFLUENT_FLUENT_PORT"):
        ip = port = None
    else:
        raise RuntimeError(
            "Please provide either ip and port data or server-info file."
        )

    return ip, port, password


def _get_running_session_mode(
    fluent_connection: _FluentConnection, mode: LaunchModes = None
):
    """Get the mode of the running session if the mode has not been mentioned
    explicitly."""
    if mode:
        session_mode = mode
    else:
        try:
            session_mode = LaunchModes.get_mode(
                fluent_connection.get_current_fluent_mode()
            )
        except BaseException:
            raise RuntimeError("Fluent session password mismatch")
    return session_mode.value[1]


def _start_instance(start_instance: Union[bool, None]):
    """Sets up how to start an instance of fluent."""
    if start_instance is None:
        return bool(
            int(
                os.getenv(
                    "PYFLUENT_START_INSTANCE", "0" if pypim.is_configured() else "1"
                )
            )
        )
    return start_instance


def _generate_launch_string(
    argvals,
    meshing_mode: bool,
    show_gui: bool,
    additional_arguments: str,
    server_info_filepath: str,
):
    """Generates the launch string to launch fluent."""
    exe_path = get_fluent_exe_path(**argvals)
    launch_string = str(exe_path)
    launch_string += _build_fluent_launch_args_string(**argvals)
    if meshing_mode:
        launch_string += " -meshing"
    launch_string += f" {additional_arguments}"
    launch_string += f' -sifile="{server_info_filepath}"'
    launch_string += " -nm"
    launch_string = _update_launch_string_wrt_gui_options(
        launch_string, show_gui, additional_arguments
    )
    return launch_string


def scm_to_py(topy):
    if not isinstance(topy, (str, list)):
        raise TypeError("Journal name should be of str or list type.")
    if isinstance(topy, str):
        topy = [topy]
    fluent_jou_arg = "".join([f'-i "{journal}" ' for journal in topy])
    return f" {fluent_jou_arg} -topy"


class LaunchFluentError(Exception):
    def __init__(self, launch_string):
        details = "\n" + "Fluent Launch string: " + launch_string
        super().__init__(details)


#   pylint: disable=unused-argument
def launch_fluent(
    product_version: str = None,
    version: str = None,
    precision: str = None,
    processor_count: int = None,
    journal_filepath: str = None,
    start_timeout: int = 100,
    additional_arguments: str = "",
    env: Dict[str, Any] = None,
    start_instance: bool = None,
    ip: str = None,
    port: int = None,
    cleanup_on_exit: bool = True,
    start_transcript: bool = True,
    show_gui: bool = None,
    case_filepath: str = None,
    case_data_filepath: str = None,
    lightweight_mode: bool = False,
    mode: Union[LaunchModes, str, None] = None,
    server_info_filepath: str = None,
    password: str = None,
    py: bool = None,
    cwd: str = None,
    topy: Union[str, list] = None,
    **kwargs,
) -> _BaseSession:
    """Launch Fluent locally in server mode or connect to a running Fluent
    server instance.

    Parameters
    ----------
    product_version : str, optional
        Version of Fluent to use in the numeric format (such as ``"23.1.0"``
        for 2023 R1). The default is ``None``, in which case the active version
        or latest installed version is used.
    version : str, optional
        Dimensions for modeling. The default is ``None``, in which case ``"3d"``
        is used. Options are ``"3d"`` and ``"2d"``.
    precision : str, optional
        Floating point precision. The default is ``None``, in which case ``"double"``
        is used. Options are ``"double"`` and ``"single"``.
    processor_count : int, optional
        Number of processors. The default is ``None``, in which case ``1``
        processor is used.  In job scheduler environments the total number of
        allocated cores is clamped to this value.
    journal_filepath : str, optional
        Name of the journal file to read. The default is ``None``.
    start_timeout : int, optional
        Maximum allowable time in seconds for connecting to the Fluent
        server. The default is ``100``.
    additional_arguments : str, optional
        Additional arguments to send to Fluent. The default is ``""``.
    env : dict[str, str], optional
        Mapping to modify environment variables in Fluent. The default
        is ``None``.
    start_instance : bool, optional
        Whether to connect to an existing Fluent instance at a specified IP
        address on a specified port. The default is ``None``, in which
        case a local instance of Fluent is started. When ``False``, use
        the next two parameters to specify the IP address and port. You
        can also use the environment variable ``PYFLUENT_START_INSTANCE=<0 or 1>``
        to set this parameter.
    ip : str, optional
        IP address for connecting to an existing Fluent instance. This parameter
        is used only when ``start_instance`` is ``False``. Otherwise, the
        IP address defaults to ``"127.0.0.1"``. You can also use the environment
        variable ``PYFLUENT_FLUENT_IP=<ip>`` to set this parameter.
    port : int, optional
        Port to listen on for an existing Fluent instance. This parameter is
        used only when ``start_instance`` is ``False``. You can use the
        environment variable ``PYFLUENT_FLUENT_PORT=<port>`` to set a default
        value.
    cleanup_on_exit : bool, optional
        Whether to shut down the connected Fluent session when PyFluent is
        exited or the ``exit()`` method is called on the session instance.
        The default is ``True``.
    start_transcript : bool, optional
        Whether to start streaming the Fluent transcript in the client. The
        default is ``True``. You can stop and start the streaming of the
        Fluent transcript subsequently via method calls on the session object.
    show_gui : bool, optional
        Whether to display the Fluent GUI when ``start_instance``
        is set to ''True``. The default is ``None`` so that explicit
        ``False`` settings can be detected. This is because you can use
        also use the environment variable ``PYFLUENT_SHOW_SERVER_GUI=<0 or 1>``
        to set this parameter. The ``show-gui`` parameter overrides the
        PYFLUENT_SHOW_SERVER_GUI environment variable. For example, if
        PYFLUENT_SHOW_SERVER_GUI is set to ``1`` and the ``show-gui``
        parameter is set to ``False``, the GUI is hidden.
    case_filepath : str, optional
        If provided, reads a fluent case file and sets the required settings
        in the fluent session
    case_data_filepath : str, optional
        If provided, reads a fluent case and data file and sets the required settings
        in the fluent session
    lightweight_mode: bool, optional
        Whether to use light io mode for reading case via ``case_filepath`` parameter.
        This parameter is used only when ``case_filepath`` is provided. The default is
        ``False``.
    mode : str, optional
        Launch mode of Fluent to point to a specific session type.
        The default value is ``None``. Options are ``"meshing"``,
        ``"pure-meshing"`` and ``"solver"``.
    server_info_filepath: str
        Path to server-info file written out by Fluent server. The default is ``None``.
    password : str, optional
            Password to connect to existing Fluent instance.
    py : bool, optional
        Passes ``"-py"`` as an additional_argument to launch fluent in python mode.
        The default is ``None``.
    cwd: str, Optional
        Path to specify current working directory to launch fluent from the defined directory as
        current working directory.
    topy: str or list, optional
        Automates scheme to python journal creation.

    Returns
    -------
    ansys.fluent.session.Session
        Fluent session.

    Notes
    -----
    In job scheduler environments such as SLURM, LSF, PBS, etc... the allocated
    machines and core counts are queried from the scheduler environment and
    passed to Fluent.
    """
    if kwargs:
        if "meshing_mode" in kwargs:
            raise RuntimeError(
                "'meshing_mode' argument is no longer used."
                " Please use launch_fluent(mode='meshing') to launch in meshing mode."
            )
        else:
            raise TypeError(
                f"launch_fluent() got an unexpected keyword argument {next(iter(kwargs))}"
            )

    del kwargs
    argvals = locals()

    new_session, meshing_mode, argvals, mode = _get_session_info(argvals, mode)
    _raise_exception_g_gu_in_windows_os(additional_arguments)
    if _start_instance(start_instance):
        server_info_filepath = _get_server_info_filepath()
        launch_string = _generate_launch_string(
            argvals, meshing_mode, show_gui, additional_arguments, server_info_filepath
        )

        try:
            LOG.info("Launching Fluent with cmd: %s", launch_string)
            sifile_last_mtime = Path(server_info_filepath).stat().st_mtime
            if env is None:
                env = {}
            if mode != LaunchModes.SOLVER_ICING:
                env["APP_LAUNCHED_FROM_CLIENT"] = "1"  # disables flserver datamodel
            kwargs = _get_subprocess_kwargs_for_fluent(env)
            if cwd:
                kwargs.update(cwd=cwd)
            if topy:
                launch_string += scm_to_py(topy)

            subprocess.Popen(launch_string, **kwargs)

            _await_fluent_launch(server_info_filepath, start_timeout, sifile_last_mtime)

            session = new_session.create_from_server_info_file(
                server_info_filepath=server_info_filepath,
                cleanup_on_exit=cleanup_on_exit,
                start_transcript=start_transcript,
                launcher_args=argvals,
            )
            if case_filepath:
                if meshing_mode:
                    session.tui.file.read_case(case_filepath)
                else:
                    session.read_case(case_filepath, lightweight_mode)
            if journal_filepath:
                if meshing_mode:
                    session.tui.file.read_journal(journal_filepath)
                else:
                    session.file.read_journal(journal_filepath)
            if case_data_filepath:
                if not meshing_mode:
                    session.file.read(
                        file_type="case-data", file_name=case_data_filepath
                    )
                else:
                    raise RuntimeError(
                        "Case and data file cannot be read in meshing mode."
                    )

            return session
        except Exception as ex:
            raise LaunchFluentError(launch_string) from ex
        finally:
            server_info_file = Path(server_info_filepath)
            if server_info_file.exists():
                server_info_file.unlink()
    else:
        if pypim.is_configured():
            LOG.info(
                "Starting Fluent remotely. The startup configuration will be ignored."
            )
            return launch_remote_fluent(
                session_cls=new_session,
                start_timeout=start_timeout,
                start_transcript=start_transcript,
                product_version="".join(get_ansys_version().split("."))[:-1],
                cleanup_on_exit=cleanup_on_exit,
                meshing_mode=meshing_mode,
                dimensionality=version,
                launcher_args=argvals,
            )
        import ansys.fluent.core as pyfluent

        if pyfluent.BUILDING_GALLERY or os.getenv("PYFLUENT_LAUNCH_CONTAINER") == "1":
            args = _build_fluent_launch_args_string(**argvals).split()
            if meshing_mode:
                args.append(" -meshing")
            # Assumes the container OS will be able to create the
            # EXAMPLES_PATH of host OS. With the Fluent docker
            # container, the following currently works only in linux.
            port, password = start_fluent_container(
                pyfluent.EXAMPLES_PATH, pyfluent.EXAMPLES_PATH, args
            )
            return new_session(
                fluent_connection=_FluentConnection(
                    start_timeout=start_timeout,
                    port=port,
                    password=password,
                    cleanup_on_exit=cleanup_on_exit,
                    start_transcript=start_transcript,
                    launcher_args=argvals,
                )
            )
        else:
            ip, port, password = _connect_to_running_server(
                argvals, server_info_filepath
            )
            fluent_connection = _FluentConnection(
                ip=ip,
                port=port,
                password=password,
                cleanup_on_exit=cleanup_on_exit,
                start_transcript=start_transcript,
                launcher_args=argvals,
            )
            new_session = _get_running_session_mode(fluent_connection, mode)
            return new_session(fluent_connection=fluent_connection)
