"""Provides a module for launching and configuring local Fluent Docker container runs.

Notes
-----

For configuration details, see :func:`configure_container_dict`, and for a list of additional Docker container run
configuration options that can also be specified through the
``container_dict`` argument for :func:`~ansys.fluent.core.launcher.launcher.launch_fluent()`,
see documentation for `Docker run`_.

For the Fluent Docker container to be able to find license information, the license file or server needs to be specified
through the ``ANSYSLMD_LICENSE_FILE`` environment variable,
or the ``license_server`` argument for the ``container_dict`` (see :func:`configure_container_dict`).

.. _Docker run: https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run

Examples
--------
Launching a Fluent Docker container with system default configuration:

>>> import ansys.fluent.core as pyfluent
>>> session = pyfluent.launch_fluent(start_container=True)

Launching with custom configuration, using ``mount_source`` and ``fluent_image``
which are arguments for :func:`configure_container_dict`, and ``auto_remove`` which is an argument for `Docker run`_:

>>> import ansys.fluent.core as pyfluent
>>> custom_config = {}
>>> custom_config.update(fluent_image='custom_fluent:v23.1.0', mount_source='/testing', auto_remove=False)
>>> session = pyfluent.launch_fluent(container_dict=custom_config)

Getting default Fluent Docker container configuration, then launching with customized configuration:

>>> import ansys.fluent.core as pyfluent
>>> config_dict = pyfluent.launch_fluent(start_container=True, dry_run=True)
Docker container run configuration information:
config_dict =
{'auto_remove': True,
 'command': ['-gu', '-sifile=/mnt/pyfluent/serverinfo-lpqsdldw.txt', '3ddp'],
 'detach': True,
 'environment': {'ANSYSLMD_LICENSE_FILE': '2048@licenseserver.com',
                 'REMOTING_PORTS': '54000/portspan=2'},
 'fluent_image': 'ghcr.io/ansys/pyfluent:v23.2.0',
 'labels': {'test_name': 'none'},
 'ports': {'54000': 54000},
 'volumes': ['/home/user/.local/share/ansys_fluent_core/examples:/mnt/pyfluent'],
 'working_dir': '/mnt/pyfluent'}
>>> config_dict.update(image_name='custom_fluent', image_tag='v23.1.0', mem_limit='1g')
>>> session = pyfluent.launch_fluent(container_dict=config_dict)
"""

import logging
import os
from pathlib import Path, PurePosixPath
import tempfile
from typing import Any, List

import ansys.fluent.core as pyfluent
from ansys.fluent.core._version import fluent_release_version
from ansys.fluent.core.session import _parse_server_info_file
from ansys.fluent.core.utils.deprecate import deprecate_argument
from ansys.fluent.core.utils.execution import timeout_loop
from ansys.fluent.core.utils.networking import get_free_port

logger = logging.getLogger("pyfluent.launcher")


class FluentImageNameTagNotSpecified(ValueError):
    """Raised when Fluent image name or image tag is not specified."""

    def __init__(self):
        """Initializes FluentImageNameTagNotSpecified."""
        super().__init__(
            "Specify either 'fluent_image' or 'image_tag' and 'image_name'."
        )


class ServerInfoFileError(ValueError):
    """Raised when server info file is not given properly."""

    def __init__(self):
        """Initializes ServerInfoFileError."""
        super().__init__(
            "Specify server info file either using 'container_server_info_file' argument or in the 'container_dict'."
        )


class LicenseServerNotSpecified(KeyError):
    """Raised when license server is not specified."""

    def __init__(self):
        """Initializes LicenseServerNotSpecified."""
        super().__init__(
            "Specify licence server either using 'ANSYSLMD_LICENSE_FILE' environment variable or in the 'container_dict'."
        )


@deprecate_argument("container_mount_path", "mount_target")
@deprecate_argument("host_mount_path", "mount_source")
def configure_container_dict(
    args: List[str],
    mount_source: str | Path | None = None,
    mount_target: str | Path | None = None,
    timeout: int = 60,
    port: int | None = None,
    license_server: str | None = None,
    container_server_info_file: str | Path | None = None,
    remove_server_info_file: bool = True,
    fluent_image: str | None = None,
    image_name: str | None = None,
    image_tag: str | None = None,
    file_transfer_service: Any | None = None,
    **container_dict,
) -> (dict, int, int, Path, bool):
    """Parses the parameters listed below, and sets up the container configuration file.

    Parameters
    ----------
    args : List[str]
        List of Fluent launch arguments.
    mount_source : str | Path, optional
        Existing path in the host operating system that will be mounted to ``mount_target``.
    mount_target : str | Path, optional
        Path inside the container where ``mount_source`` will be mounted to.
    timeout : int, optional
        Time limit  for the Fluent container to start, in seconds. By default, 30 seconds.
    port : int, optional
        Port for Fluent container to use.
    license_server : str, optional
        License server for Ansys Fluent to use.
    container_server_info_file : str | Path, optional
        Name of the server information file for Fluent to write on the ``mount_source``.
    remove_server_info_file : bool, optional
        Defaults to True, and automatically deletes the server information file after PyFluent has finished using it.
    fluent_image : str, optional
        Specifies full image name for Docker container run, with the format ``"image_name:image_tag"``.
        ``image_tag`` and ``image_name`` are ignored if ``fluent_image`` has been specified.
    image_name : str, optional
        Ignored if ``fluent_image`` has been specified.
    image_tag : str, optional
        Ignored if ``fluent_image`` has been specified.
    file_transfer_service : optional
        Supports file upload and download.
    **container_dict
        Additional keyword arguments can be specified, they will be treated as Docker container run options
        to be passed directly to the Docker run execution. See examples below and `Docker run`_ documentation.

    Returns
    -------
    fluent_image : str
    container_dict : dict
    timeout : int
    port : int
    host_server_info_file : Path
    remove_server_info_file: bool

    Raises
    ------
    LicenseServerNotSpecified
        If license server is not specified through an environment variable or in ``container_dict``.
    ServerInfoFileError
        If server info file is specified through both a command-line argument inside ``container_dict`` and the  ``container_server_info_file`` parameter.
    FluentImageNameTagNotSpecified
        If ``fluent_image`` or ``image_tag`` and ``image_name`` are not specified.

    Notes
    -----
    This function should usually not be called directly, it is automatically used by
    :func:`~ansys.fluent.core.launcher.launcher.launch_fluent()`.

    For a list of additional Docker container run configuration options that can also be specified using
    ``container_dict``, see `Docker run`_ documentation.

    See also :func:`start_fluent_container`.
    """

    if (
        container_dict
        and "environment" in container_dict
        and os.getenv("PYFLUENT_HIDE_LOG_SECRETS") == "1"
    ):
        container_dict_h = container_dict.copy()
        container_dict_h.pop("environment")
        logger.debug(f"container_dict before processing: {container_dict_h}")
        del container_dict_h
    else:
        logger.debug(f"container_dict before processing: {container_dict}")

    if not mount_source:
        if file_transfer_service:
            mount_source = file_transfer_service.MOUNT_SOURCE
        else:
            mount_source = os.getenv(
                "PYFLUENT_CONTAINER_MOUNT_SOURCE",
                pyfluent.CONTAINER_MOUNT_SOURCE or os.getcwd(),
            )

    elif "volumes" in container_dict:
        logger.warning(
            "'volumes' keyword specified in 'container_dict', but "
            "it is going to be overwritten by specified 'mount_source'."
        )
        container_dict.pop("volumes")

    if not os.path.exists(mount_source):
        os.makedirs(mount_source)

    if not mount_target:
        mount_target = os.getenv(
            "PYFLUENT_CONTAINER_MOUNT_TARGET", pyfluent.CONTAINER_MOUNT_TARGET
        )
    elif "volumes" in container_dict:
        logger.warning(
            "'volumes' keyword specified in 'container_dict', but "
            "it is going to be overwritten by specified 'mount_target'."
        )
        container_dict.pop("volumes")

    if "volumes" not in container_dict:
        container_dict.update(volumes=[f"{mount_source}:{mount_target}"])
    else:
        logger.debug(f"container_dict['volumes']: {container_dict['volumes']}")
        if len(container_dict["volumes"]) != 1:
            logger.warning(
                "Multiple volumes being mounted in the Docker container, "
                "using the first mount as the working directory for Fluent."
            )
        volumes_string = container_dict["volumes"][0]
        mount_target = ""
        for c in reversed(volumes_string):
            if c == ":":
                break
            else:
                mount_target += c
        mount_target = mount_target[::-1]
        mount_source = volumes_string.replace(":" + mount_target, "")
        logger.debug(f"mount_source: {mount_source}")
        logger.debug(f"mount_target: {mount_target}")
    logger.warning(
        f"Starting Fluent container mounted to {mount_source}, with this path available as {mount_target} for the Fluent session running inside the container."
    )
    port_mapping = {port: port} if port else {}
    if not port_mapping and "ports" in container_dict:
        # take the specified 'port', OR the first port value from the specified 'ports', for Fluent to use
        port_mapping = container_dict["ports"]
    if not port_mapping and pyfluent.LAUNCH_FLUENT_PORT:
        port = pyfluent.LAUNCH_FLUENT_PORT
        port_mapping = {port: port}
    if not port_mapping:
        port = get_free_port()
        port_mapping = {port: port}

    container_dict.update(
        ports={str(x): y for x, y in port_mapping.items()}
    )  # container port : host port
    container_grpc_port = next(
        iter(port_mapping.values())
    )  # the first port in the mapping is chosen as the gRPC port

    if "environment" not in container_dict:
        if not license_server:
            license_server = os.getenv("ANSYSLMD_LICENSE_FILE")

        if not license_server:
            raise LicenseServerNotSpecified()
        container_dict.update(
            environment={
                "ANSYSLMD_LICENSE_FILE": license_server,
                "REMOTING_PORTS": f"{container_grpc_port}/portspan=2",
            }
        )

    if "labels" not in container_dict:
        test_name = os.getenv("PYFLUENT_TEST_NAME", "none")
        container_dict.update(
            labels={"test_name": test_name},
        )

    if "working_dir" not in container_dict:
        container_dict.update(
            working_dir=mount_target,
        )

    if "command" in container_dict:
        for v in container_dict["command"]:
            if v.startswith("-sifile="):
                if container_server_info_file:
                    raise ServerInfoFileError()
                container_server_info_file = PurePosixPath(
                    v.replace("-sifile=", "")
                ).name
                logger.debug(
                    f"Found server info file specification for {container_server_info_file}."
                )

    if container_server_info_file:
        container_server_info_file = (
            PurePosixPath(mount_target) / PurePosixPath(container_server_info_file).name
        )
    else:
        fd, sifile = tempfile.mkstemp(
            suffix=".txt", prefix="serverinfo-", dir=mount_source
        )
        os.close(fd)
        container_server_info_file = PurePosixPath(mount_target) / Path(sifile).name

    if not fluent_image:
        if not image_tag:
            image_tag = os.getenv("FLUENT_IMAGE_TAG", f"v{fluent_release_version}")
        if not image_name:
            image_name = os.getenv("FLUENT_IMAGE_NAME", "ghcr.io/ansys/pyfluent")
        if not image_tag or not image_name:
            fluent_image = os.getenv("FLUENT_CONTAINER_IMAGE", None)
        elif image_tag and image_name:
            if image_tag.startswith("sha"):
                fluent_image = f"{image_name}@{image_tag}"
            else:
                fluent_image = f"{image_name}:{image_tag}"
        else:
            raise FluentImageNameTagNotSpecified()

    container_dict["fluent_image"] = fluent_image

    if not pyfluent.FLUENT_AUTOMATIC_TRANSCRIPT:
        if "environment" not in container_dict:
            container_dict["environment"] = {}
        container_dict["environment"]["FLUENT_NO_AUTOMATIC_TRANSCRIPT"] = "1"

    if os.getenv("REMOTING_NEW_DM_API") == "1":
        if "environment" not in container_dict:
            container_dict["environment"] = {}
        container_dict["environment"]["REMOTING_NEW_DM_API"] = "1"

    if pyfluent.LAUNCH_FLUENT_IP or os.getenv("REMOTING_SERVER_ADDRESS"):
        if "environment" not in container_dict:
            container_dict["environment"] = {}
        container_dict["environment"]["REMOTING_SERVER_ADDRESS"] = (
            pyfluent.LAUNCH_FLUENT_IP or os.getenv("REMOTING_SERVER_ADDRESS")
        )

    if pyfluent.LAUNCH_FLUENT_SKIP_PASSWORD_CHECK:
        if "environment" not in container_dict:
            container_dict["environment"] = {}
        container_dict["environment"]["FLUENT_LAUNCHED_FROM_PYFLUENT"] = "1"

    fluent_commands = [f"-sifile={container_server_info_file}"] + args

    container_dict_default = {}
    container_dict_default.update(
        command=fluent_commands,
        detach=True,
        auto_remove=True,
    )

    for k, v in container_dict_default.items():
        if k not in container_dict:
            container_dict[k] = v

    host_server_info_file = Path(mount_source) / container_server_info_file.name

    return (
        container_dict,
        timeout,
        container_grpc_port,
        host_server_info_file,
        remove_server_info_file,
    )


def start_fluent_container(
    args: List[str], container_dict: dict | None = None
) -> tuple[int, str, Any]:
    """Start a Fluent container.

    Parameters
    ----------
    args : List[str]
        List of Fluent launch arguments.
    container_dict : dict, optional
        Dictionary with Docker container configuration.

    Returns
    -------
    int
        Fluent gPRC server port exposed from the container.
    str
        Fluent gPRC server password exposed from the container.

    Raises
    ------
    TimeoutError
        If Fluent container launch reaches timeout.

    Notes
    -----
    Uses :func:`configure_container_dict` to parse the optional ``container_dict`` configuration.

    This function should usually not be called directly, it is automatically used by
    :func:`~ansys.fluent.core.launcher.launcher.launch_fluent()`.
    """

    if container_dict is None:
        container_dict = {}

    container_vars = configure_container_dict(args, **container_dict)

    (
        config_dict,
        timeout,
        port,
        host_server_info_file,
        remove_server_info_file,
    ) = container_vars

    if os.getenv("PYFLUENT_HIDE_LOG_SECRETS") != "1":
        logger.debug(f"container_vars: {container_vars}")
    else:
        config_dict_h = config_dict.copy()
        config_dict_h.pop("environment")
        container_vars_tmp = (
            config_dict_h,
            timeout,
            port,
            host_server_info_file,
            remove_server_info_file,
        )
        logger.debug(f"container_vars: {container_vars_tmp}")
        del container_vars_tmp

    try:
        if not host_server_info_file.exists():
            host_server_info_file.parents[0].mkdir(exist_ok=True)

        host_server_info_file.touch(exist_ok=True)
        last_mtime = host_server_info_file.stat().st_mtime

        import docker

        docker_client = docker.from_env()

        logger.debug("Starting Fluent docker container...")

        container = docker_client.containers.run(
            config_dict.pop("fluent_image"), **config_dict
        )

        success = timeout_loop(
            lambda: host_server_info_file.stat().st_mtime > last_mtime, timeout
        )

        if not success:
            raise TimeoutError(
                "Fluent container launch has timed out, stop container manually."
            )
        else:
            _, _, password = _parse_server_info_file(str(host_server_info_file))

            return port, password, container
    finally:
        if remove_server_info_file and host_server_info_file.exists():
            host_server_info_file.unlink()
