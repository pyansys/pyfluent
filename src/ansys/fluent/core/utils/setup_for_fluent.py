from ansys.fluent.core.launcher.launcher import (
    FluentVersion,
    launch_fluent,
    set_ansys_version,
)
from ansys.fluent.core.session_solver import Solver


def setup_for_fluent(*args, **kwargs):
    """Returns global PyConsole objects."""

    if kwargs["product_version"] == "22.2.0":
        set_ansys_version(FluentVersion.version_22R2)
    elif kwargs["product_version"] == "23.1.0":
        set_ansys_version(FluentVersion.version_23R1)

    del kwargs["product_version"]

    session = launch_fluent(*args, **kwargs)
    globals = {}
    if "mode" in kwargs.keys() and kwargs["mode"] == "meshing":
        globals["meshing"] = session.meshing
        globals["workflow"] = session.workflow
        globals["PartManagement"] = session.PartManagement
        globals["PMFileManagement"] = session.PMFileManagement
        globals["preferences"] = session.preferences
        globals["solver"] = Solver(fluent_connection=session.fluent_connection)
    elif "mode" in kwargs.keys() and kwargs["mode"] == "solver":
        globals["solver"] = session
        globals["preferences"] = session.preferences
    return globals
