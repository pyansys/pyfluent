import pytest
from util.meshing_workflow import new_mesh_session  # noqa: F401
from util.solver_workflow import new_solver_session  # noqa: F401

from ansys.fluent.core import examples

import_file_name = examples.download_file(
    "mixing_elbow.msh.h5", "pyfluent/mixing_elbow"
)


def test_meshing_session_upload(new_mesh_session):
    session = new_mesh_session
    with pytest.raises(ConnectionError) as e_info:
        session.remote_file_handler.upload(import_file_name)
    session.exit()


def test_meshing_session_download(new_mesh_session):
    session = new_mesh_session
    with pytest.raises(ConnectionError) as e_info:
        session.remote_file_handler.download(import_file_name)
    session.exit()


def test_solver_session_upload(new_solver_session):
    session = new_solver_session
    with pytest.raises(ConnectionError) as e_info:
        session.remote_file_handler.upload(import_file_name)
    session.exit()


def test_solver_session_download(new_solver_session):
    session = new_solver_session
    with pytest.raises(ConnectionError) as e_info:
        session.remote_file_handler.download(import_file_name)
    session.exit()
