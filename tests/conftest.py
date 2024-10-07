from contextlib import nullcontext
import functools
import operator
import os

from packaging.specifiers import SpecifierSet
from packaging.version import Version
import pytest

import ansys.fluent.core as pyfluent
from ansys.fluent.core import codegen
from ansys.fluent.core.examples.downloads import download_file
from ansys.fluent.core.utils.file_transfer_service import RemoteFileTransferStrategy
from ansys.fluent.core.utils.fluent_version import FluentVersion

_fluent_release_version = FluentVersion.current_release().value


def pytest_addoption(parser):
    parser.addoption(
        "--fluent-version",
        action="store",
        metavar="VERSION",
        help="only run tests supported by Fluent version VERSION.",
    )
    parser.addoption(
        "--nightly", action="store_true", default=False, help="run nightly tests"
    )
    parser.addoption(
        "--solvermode", action="store_true", default=False, help="run solvermode tests"
    )


def pytest_runtest_setup(item):
    if (
        any(mark.name == "standalone" for mark in item.iter_markers())
        and os.getenv("PYFLUENT_LAUNCH_CONTAINER") == "1"
    ):
        pytest.skip()

    is_nightly = item.config.getoption("--nightly")
    if not is_nightly and any(mark.name == "nightly" for mark in item.iter_markers()):
        pytest.skip()

    is_solvermode_option = item.config.getoption("--solvermode")
    is_solvermode_path = "test_solvermode" in item.path.parts
    if is_solvermode_option ^ is_solvermode_path:
        pytest.skip()

    version_specs = []
    for mark in item.iter_markers(name="fluent_version"):
        spec = mark.args[0]
        # if a test is marked as fluent_version("latest")
        # run with dev and release Fluent versions in nightly
        # run with release Fluent versions in PRs
        if spec == "latest":
            spec = (
                f">={_fluent_release_version}"
                if is_nightly or is_solvermode_option
                else f"=={_fluent_release_version}"
            )
        version_specs.append(SpecifierSet(spec))
    if version_specs:
        combined_spec = functools.reduce(operator.and_, version_specs)
        version = item.config.getoption("--fluent-version")
        if version and Version(version) not in combined_spec:
            pytest.skip()


@pytest.fixture(autouse=True)
def run_before_each_test(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> None:
    monkeypatch.setenv("PYFLUENT_TEST_NAME", request.node.name)
    pyfluent.CONTAINER_MOUNT_SOURCE = pyfluent.EXAMPLES_PATH
    pyfluent.CONTAINER_MOUNT_TARGET = pyfluent.EXAMPLES_PATH
    codegen.CODEGEN_GENERATE_BUILTIN_SETTINGS = False


class Helpers:
    """Can be reused to provide helper methods to tests."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch):
        self.monkeypatch = monkeypatch

    def mock_awp_vars(self, version=None):
        """Activates env vars for Fluent versions up to specified version, deactivates
        env vars for versions newer than specified."""
        if not version:
            version = FluentVersion.current_release()
        elif not isinstance(version, FluentVersion):
            version = FluentVersion(version)
        self.monkeypatch.delenv("PYFLUENT_FLUENT_ROOT", raising=False)
        for fv in FluentVersion:
            if fv <= version:
                self.monkeypatch.setenv(fv.awp_var, f"ansys_inc/{fv.name}")
            else:
                self.monkeypatch.delenv(fv.awp_var, raising=False)

    def delete_all_awp_vars(self):
        for fv in FluentVersion:
            self.monkeypatch.delenv(fv.awp_var, raising=False)


@pytest.fixture
def helpers(monkeypatch):
    return Helpers(monkeypatch)


pytest.wont_raise = nullcontext


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 5:
        session.exitstatus = 0


# tests_by_fixture = defaultdict(list)


# def pytest_collection_finish(session):
#     for k, v in sorted(tests_by_fixture.items(), key=lambda t: len(t[1]), reverse=True):
#         print(k, len(v))


# def pytest_itemcollected(item):
#     if not item.nodeid.startswith("tests/test_solvermode/"):
#         for fixture in item.fixturenames:
#             tests_by_fixture[fixture].append(item.nodeid)


@pytest.fixture
def mixing_elbow_geometry_filename():
    return download_file(
        file_name="mixing_elbow.pmdb", directory="pyfluent/mixing_elbow"
    )


@pytest.fixture
def exhaust_system_geometry_filename():
    return download_file(
        file_name="exhaust_system.fmd", directory="pyfluent/exhaust_system"
    )


def create_session(**kwargs):
    if pyfluent.USE_FILE_TRANSFER_SERVICE:
        container_dict = {"mount_source": file_transfer_service.MOUNT_SOURCE}
        file_transfer_service = RemoteFileTransferStrategy()
        return pyfluent.launch_fluent(
            container_dict=container_dict,
            file_transfer_service=file_transfer_service,
            **kwargs,
        )
    else:
        return pyfluent.launch_fluent(**kwargs)


@pytest.fixture
def new_meshing_session():
    meshing = create_session(mode=pyfluent.FluentMode.MESHING)
    yield meshing
    meshing.exit()


@pytest.fixture
def new_pure_meshing_session():
    meshing = create_session(mode=pyfluent.FluentMode.PURE_MESHING)
    yield meshing
    meshing.exit()


@pytest.fixture
def watertight_workflow_session(new_meshing_session):
    new_meshing_session.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    return new_meshing_session


@pytest.fixture
def fault_tolerant_workflow_session(new_meshing_session):
    new_meshing_session.workflow.InitializeWorkflow(
        WorkflowType="Fault-tolerant Meshing"
    )
    return new_meshing_session


@pytest.fixture
def mixing_elbow_watertight_pure_meshing_session(
    new_pure_meshing_session, mixing_elbow_geometry_filename
):
    meshing = new_pure_meshing_session
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    meshing.workflow.TaskObject["Import Geometry"].Arguments = dict(
        FileName=mixing_elbow_geometry_filename, LengthUnit="in"
    )

    return meshing


@pytest.fixture
def new_meshing_session_new_api_enabled():
    meshing = create_session(
        mode=pyfluent.FluentMode.MESHING, enable_data_model_api_upgrades=True
    )
    yield meshing
    meshing.exit()


@pytest.fixture
def new_solver_session():
    solver = create_session()
    yield solver
    solver.exit()


@pytest.fixture
def new_solver_session_sp():
    solver = create_session(precision="single")
    yield solver
    solver.exit()


@pytest.fixture
def new_solver_session_2d():
    solver = create_session(dimension=2)
    yield solver
    solver.exit()


@pytest.fixture
def static_mixer_settings_session(new_solver_session):
    solver = new_solver_session
    case_name = download_file("Static_Mixer_main.cas.h5", "pyfluent/static_mixer")
    solver.file.read(
        file_type="case",
        file_name=case_name,
        lightweight_setup=True,
    )
    return solver


@pytest.fixture
def static_mixer_case_session(new_solver_session):
    solver = new_solver_session
    case_name = download_file("Static_Mixer_main.cas.h5", "pyfluent/static_mixer")
    solver.file.read(file_type="case", file_name=case_name)
    return solver


@pytest.fixture
def mixing_elbow_settings_session(new_solver_session):
    solver = new_solver_session
    case_name = download_file("mixing_elbow.cas.h5", "pyfluent/mixing_elbow")
    solver.settings.file.read(
        file_type="case",
        file_name=case_name,
        lightweight_setup=True,
    )
    return solver


@pytest.fixture
def mixing_elbow_case_data_session(new_solver_session):
    solver = new_solver_session
    case_name = download_file("mixing_elbow.cas.h5", "pyfluent/mixing_elbow")
    download_file("mixing_elbow.dat.h5", "pyfluent/mixing_elbow")
    solver.settings.file.read(file_type="case-data", file_name=case_name)
    return solver


@pytest.fixture
def mixing_elbow_param_case_data_session(new_solver_session):
    solver = new_solver_session
    case_name = download_file("elbow_param.cas.h5", "pyfluent/mixing_elbow")
    download_file("elbow_param.dat.h5", "pyfluent/mixing_elbow")
    solver.settings.file.read(file_type="case-data", file_name=case_name)
    return solver


@pytest.fixture
def disk_settings_session(new_solver_session_2d):
    solver = new_solver_session_2d
    case_name = download_file("disk.cas.h5", "pyfluent/rotating_disk")
    solver.file.read(
        file_type="case",
        file_name=case_name,
        lightweight_setup=True,
    )
    return solver


@pytest.fixture
def disk_case_session(new_solver_session_2d):
    solver = new_solver_session_2d
    case_name = download_file("disk.cas.h5", "pyfluent/rotating_disk")
    solver.file.read(file_type="case", file_name=case_name)
    return solver


@pytest.fixture
def periodic_rot_settings_session(new_solver_session):
    solver = new_solver_session
    case_name = download_file(
        "periodic_rot.cas.h5",
        "pyfluent/periodic_rot",
    )
    solver.file.read(
        file_type="case",
        file_name=case_name,
        lightweight_setup=True,
    )
    return solver
