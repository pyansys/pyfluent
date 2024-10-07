"""Provides a module for launching Fluent in standalone mode.

Examples
--------

>>> from ansys.fluent.core.launcher.launcher import create_launcher
>>> from ansys.fluent.core.launcher.pyfluent_enums import LaunchMode, FluentMode

>>> standalone_meshing_launcher = create_launcher(LaunchMode.STANDALONE, mode=FluentMode.MESHING)
>>> standalone_meshing_session = standalone_meshing_launcher()

>>> standalone_solver_launcher = create_launcher(LaunchMode.STANDALONE)
>>> standalone_solver_session = standalone_solver_launcher()
"""

import logging
import os
from pathlib import Path
import subprocess
from typing import Any, Dict

from ansys.fluent.core.launcher.error_handler import (
    LaunchFluentError,
    _raise_non_gui_exception_in_windows,
)
from ansys.fluent.core.launcher.launcher_utils import (
    _await_fluent_launch,
    _build_journal_argument,
    _confirm_watchdog_start,
    _get_subprocess_kwargs_for_fluent,
    is_windows,
)
from ansys.fluent.core.launcher.process_launch_string import _generate_launch_string
from ansys.fluent.core.launcher.pyfluent_enums import (
    Dimension,
    FluentLinuxGraphicsDriver,
    FluentMode,
    FluentWindowsGraphicsDriver,
    Precision,
    UIMode,
    _get_argvals_and_session,
    _get_standalone_launch_fluent_version,
)
from ansys.fluent.core.launcher.server_info import (
    _get_server_info,
    _get_server_info_file_name,
)
import ansys.fluent.core.launcher.watchdog as watchdog
from ansys.fluent.core.utils.fluent_version import FluentVersion

logger = logging.getLogger("pyfluent.launcher")


class StandaloneLauncher:
    """Instantiates Fluent session in standalone mode."""

    def __init__(
        self,
        mode: FluentMode | str | None = None,
        ui_mode: UIMode | str | None = None,
        graphics_driver: (
            FluentWindowsGraphicsDriver | FluentLinuxGraphicsDriver | str
        ) = None,
        product_version: FluentVersion | str | float | int | None = None,
        dimension: Dimension | int | None = None,
        precision: Precision | str | None = None,
        processor_count: int | None = None,
        journal_file_names: None | str | list[str] = None,
        start_timeout: int = 60,
        additional_arguments: str | None = "",
        env: Dict[str, Any] | Path | None = None,
        cleanup_on_exit: bool = True,
        dry_run: bool = False,
        start_transcript: bool = True,
        case_file_name: str | None = None,
        case_data_file_name: str | None = None,
        lightweight_mode: bool | None = None,
        py: bool | None = None,
        gpu: bool | None = None,
        cwd: str | None = None,
        fluent_path: str | None = None,
        topy: str | list | None = None,
        start_watchdog: bool | None = None,
        file_transfer_service: Any | None = None,
        enable_data_model_api_upgrades: bool | None = None,
    ):
        """Launch Fluent session in standalone mode.

        Parameters
        ----------
        mode : FluentMode
            Launch mode of Fluent to point to a specific session type.
        ui_mode : UIMode
            Fluent user interface mode. Options are the values of the ``UIMode`` enum.
        graphics_driver : FluentWindowsGraphicsDriver or FluentLinuxGraphicsDriver
            Graphics driver of Fluent. Options are the values of the
            ``FluentWindowsGraphicsDriver`` enum in Windows or the values of the
            ``FluentLinuxGraphicsDriver`` enum in Linux.
        product_version : FluentVersion or str or float or int, optional
            Version of Ansys Fluent to launch. To use Fluent version 2024 R2, pass
           ``FluentVersion.v242``, ``"24.2.0"``, ``"24.2"``, ``24.2``, or ``242``.
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
            server. The default is ``60``.
        additional_arguments : str, optional
            Additional arguments to send to Fluent as a string in the same
            format they are normally passed to Fluent on the command line.
        env : dict[str, str], optional
            Mapping to modify environment variables in Fluent. The default
            is ``None``.
        cleanup_on_exit : bool, optional
            Whether to shut down the connected Fluent session when PyFluent is
            exited, or the ``exit()`` method is called on the session instance,
            or if the session instance becomes unreferenced. The default is ``True``.
        dry_run : bool, optional
            Defaults to False. If True, will not launch Fluent, and will instead print configuration information
            that would be used as if Fluent was being launched.
        start_transcript : bool, optional
            Whether to start streaming the Fluent transcript in the client. The
            default is ``True``. You can stop and start the streaming of the
            Fluent transcript subsequently via the method calls, ``transcript.start()``
            and ``transcript.stop()`` on the session object.
        case_file_name : str, optional
            Name of the case file to read into the
            Fluent session. The default is ``None``.
        case_data_file_name : str, optional
            Name of the case data file. If names of both a case file and case data file are provided, they are read into the Fluent session.
        lightweight_mode : bool, optional
            Whether to run in lightweight mode. In lightweight mode, the lightweight settings are read into the
            current Fluent solver session. The mesh is read into a background Fluent solver session which will
            replace the current Fluent solver session once the mesh read is complete and the lightweight settings
            made by the user in the current Fluent solver session have been applied in the background Fluent
            solver session. This is all orchestrated by PyFluent and requires no special usage.
            This parameter is used only when ``case_file_name`` is provided. The default is ``False``.
        py : bool, optional
            If True, Fluent will run in Python mode. Default is None.
        gpu : bool, optional
            If True, Fluent will start with GPU Solver.
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
        file_transfer_service : optional
            File transfer service. Uploads/downloads files to/from the server.
        enable_data_model_api_upgrades: Optional[bool] = None,
            This option enables experimental code in Fluent, which provides further
            improvements to the enhanced meshing workflow API.
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
        self.argvals, self.new_session = _get_argvals_and_session(locals().copy())
        self.file_transfer_service = file_transfer_service
        if os.getenv("PYFLUENT_SHOW_SERVER_GUI") == "1":
            ui_mode = UIMode.GUI
        self.argvals["ui_mode"] = UIMode(ui_mode)
        if self.argvals["start_timeout"] is None:
            self.argvals["start_timeout"] = 60
        if self.argvals["lightweight_mode"] is None:
            self.argvals["lightweight_mode"] = False
        fluent_version = _get_standalone_launch_fluent_version(
            self.argvals["product_version"]
        )
        if fluent_version:
            _raise_non_gui_exception_in_windows(self.argvals["ui_mode"], fluent_version)

        if fluent_version and fluent_version >= FluentVersion.v251:
            self.argvals["py"] = True

        if os.getenv("PYFLUENT_FLUENT_DEBUG") == "1":
            self.argvals["fluent_debug"] = True

        self._server_info_file_name = _get_server_info_file_name()
        self._launch_string = _generate_launch_string(
            self.argvals,
            self._server_info_file_name,
        )

        self._sifile_last_mtime = Path(self._server_info_file_name).stat().st_mtime
        self._kwargs = _get_subprocess_kwargs_for_fluent(
            self.argvals["env"], self.argvals
        )
        if self.argvals["cwd"]:
            self._kwargs.update(cwd=self.argvals["cwd"])
        self._launch_string += _build_journal_argument(
            self.argvals["topy"], self.argvals["journal_file_names"]
        )

        if is_windows():
            # Using 'start.exe' is better; otherwise Fluent is more susceptible to bad termination attempts.
            self._launch_cmd = 'start "" ' + self._launch_string
        else:
            if self.argvals["ui_mode"] not in [UIMode.GUI, UIMode.HIDDEN_GUI]:
                # Using nohup to hide Fluent output from the current terminal
                self._launch_cmd = "nohup " + self._launch_string + " &"
            else:
                self._launch_cmd = self._launch_string

    def __call__(self):
        if self.argvals["dry_run"]:
            print(f"Fluent launch string: {self._launch_string}")
            return
        try:
            logger.debug(f"Launching Fluent with command: {self._launch_cmd}")

            subprocess.Popen(self._launch_cmd, **self._kwargs)

            try:
                _await_fluent_launch(
                    self._server_info_file_name,
                    self.argvals["start_timeout"],
                    self._sifile_last_mtime,
                )
            except TimeoutError as ex:
                if is_windows():
                    logger.warning(f"Exception caught - {type(ex).__name__}: {ex}")
                    launch_cmd = self._launch_string.replace('"', "", 2)
                    self._kwargs.update(shell=False)
                    logger.warning(
                        f"Retrying Fluent launch with less robust command: {launch_cmd}"
                    )
                    subprocess.Popen(launch_cmd, **self._kwargs)
                    _await_fluent_launch(
                        self._server_info_file_name,
                        self.argvals["start_timeout"],
                        self._sifile_last_mtime,
                    )
                else:
                    raise ex

            session = self.new_session._create_from_server_info_file(
                server_info_file_name=self._server_info_file_name,
                file_transfer_service=self.file_transfer_service,
                cleanup_on_exit=self.argvals["cleanup_on_exit"],
                start_transcript=self.argvals["start_transcript"],
                launcher_args=self.argvals,
                inside_container=False,
            )
            start_watchdog = _confirm_watchdog_start(
                self.argvals["start_watchdog"],
                self.argvals["cleanup_on_exit"],
                session._fluent_connection,
            )
            if start_watchdog:
                logger.info("Launching Watchdog for local Fluent client...")
                ip, port, password = _get_server_info(self._server_info_file_name)
                watchdog.launch(os.getpid(), port, password, ip)
            if self.argvals["case_file_name"]:
                if FluentMode.is_meshing(self.argvals["mode"]):
                    session.tui.file.read_case(self.argvals["case_file_name"])
                elif self.argvals["lightweight_mode"]:
                    session.read_case_lightweight(self.argvals["case_file_name"])
                else:
                    session.file.read(
                        file_type="case",
                        file_name=self.argvals["case_file_name"],
                    )
            if self.argvals["case_data_file_name"]:
                if not FluentMode.is_meshing(self.argvals["mode"]):
                    session.file.read(
                        file_type="case-data",
                        file_name=self.argvals["case_data_file_name"],
                    )
                else:
                    raise RuntimeError(
                        "Case and data file cannot be read in meshing mode."
                    )

            return session
        except Exception as ex:
            logger.error(f"Exception caught - {type(ex).__name__}: {ex}")
            raise LaunchFluentError(self._launch_cmd) from ex
        finally:
            server_info_file = Path(self._server_info_file_name)
            if server_info_file.exists():
                server_info_file.unlink()
