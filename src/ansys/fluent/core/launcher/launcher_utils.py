"""Provides a module for launching utilities."""

import logging
import os
from pathlib import Path
import platform
import socket
import subprocess
import time
from typing import Any, Dict

from ansys.fluent.core.exceptions import InvalidArgument
from ansys.fluent.core.utils.networking import find_remoting_ip

logger = logging.getLogger("pyfluent.launcher")


def is_windows():
    """Check if the current operating system is Windows."""
    return platform.system() == "Windows"


def _get_subprocess_kwargs_for_fluent(env: Dict[str, Any], argvals) -> Dict[str, Any]:
    scheduler_options = argvals.get("scheduler_options")
    is_slurm = scheduler_options and scheduler_options["scheduler"] == "slurm"
    kwargs: Dict[str, Any] = {}
    if is_slurm:
        kwargs.update(stdout=subprocess.PIPE)
    if is_windows():
        kwargs.update(shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        kwargs.update(shell=True, start_new_session=True)
    fluent_env = os.environ.copy()
    fluent_env.update({k: str(v) for k, v in env.items()})
    fluent_env["REMOTING_THROW_LAST_TUI_ERROR"] = "1"

    if argvals.get("enable_data_model_api_upgrades") is True:
        fluent_env["REMOTING_NEW_DM_API"] = "1"

    if not is_slurm:
        from ansys.fluent.core import INFER_REMOTING_IP

        if INFER_REMOTING_IP and not "REMOTING_SERVER_ADDRESS" in fluent_env:
            remoting_ip = find_remoting_ip()
            if remoting_ip:
                fluent_env["REMOTING_SERVER_ADDRESS"] = remoting_ip

    kwargs.update(env=fluent_env)

    return kwargs


def _await_fluent_launch(
    server_info_file_name: str, start_timeout: int, sifile_last_mtime: float
):
    """Wait for successful fluent launch or raise an error."""
    while True:
        if Path(server_info_file_name).stat().st_mtime > sifile_last_mtime:
            time.sleep(1)
            logger.info("Fluent has been successfully launched.")
            break
        if start_timeout == 0:
            raise TimeoutError("The launch process has timed out.")
        time.sleep(1)
        start_timeout -= 1
        logger.info("Waiting for Fluent to launch...")
        if start_timeout >= 0:
            logger.info(f"...{start_timeout} seconds remaining")


def _confirm_watchdog_start(start_watchdog, cleanup_on_exit, fluent_connection):
    """Confirm whether Fluent is running locally, and whether the Watchdog should be
    started."""
    if start_watchdog is None and cleanup_on_exit:
        host = fluent_connection.connection_properties.cortex_host
        if host == socket.gethostname():
            logger.debug(
                "Fluent running on the host machine and 'cleanup_on_exit' activated, will launch Watchdog."
            )
            start_watchdog = True
    return start_watchdog


def _build_journal_argument(
    topy: None | bool | str, journal_file_names: None | str | list[str]
) -> str:
    """Build Fluent commandline journal argument."""

    from beartype import BeartypeConf, beartype

    @beartype(conf=BeartypeConf(violation_type=TypeError))
    def _impl(
        topy: None | bool | str, journal_file_names: None | str | list[str]
    ) -> str:
        if topy and not journal_file_names:
            raise InvalidArgument(
                "Use 'journal_file_names' to specify and convert journal files."
            )
        fluent_jou_arg = ""
        if isinstance(journal_file_names, str):
            journal_file_names = [journal_file_names]
        if journal_file_names:
            fluent_jou_arg += "".join(
                [f' -i "{journal}"' for journal in journal_file_names]
            )
        if topy:
            if isinstance(topy, str):
                fluent_jou_arg += f' -topy="{topy}"'
            else:
                fluent_jou_arg += " -topy"
        return fluent_jou_arg

    return _impl(topy, journal_file_names)
