"""Module containing class encapsulating Fluent connection."""


from asyncio import Future
import functools
import importlib
import logging
import threading
from typing import Any, Optional

from ansys.fluent.core.services.datamodel_se import PyMenuGeneric
from ansys.fluent.core.services.datamodel_tui import TUIMenu
from ansys.fluent.core.services.reduction import Reduction, ReductionService
from ansys.fluent.core.services.svar import SVARData, SVARInfo, SVARService
from ansys.fluent.core.session import _CODEGEN_MSG_TUI, BaseSession, _get_preferences
from ansys.fluent.core.session_shared import _CODEGEN_MSG_DATAMODEL
from ansys.fluent.core.solver.flobject import (
    Group,
    NamedObject,
    SettingsBase,
    StateType,
)
from ansys.fluent.core.solver.flobject import get_root as settings_get_root
import ansys.fluent.core.solver.function.reduction as reduction_old
from ansys.fluent.core.systemcoupling import SystemCoupling
from ansys.fluent.core.utils.execution import asynchronous
from ansys.fluent.core.utils.fluent_version import get_version_for_file_name
from ansys.fluent.core.workflow import WorkflowWrapper

tui_logger = logging.getLogger("pyfluent.tui")
datamodel_logger = logging.getLogger("pyfluent.datamodel")


def _set_state_safe(obj: SettingsBase, state: StateType):
    try:
        obj.set_state(state)
    except RuntimeError:
        if isinstance(obj, NamedObject):
            for k, v in state.items():
                _set_state_safe(obj[k], v)
        elif isinstance(obj, Group):
            for k, v in state.items():
                _set_state_safe(getattr(obj, k), v)
        else:
            datamodel_logger.debug(f"set_state failed at {obj.path}")


class Solver(BaseSession):
    """Encapsulates a Fluent solver session.

    A ``tui`` object for solver TUI
    commanding, and solver settings objects are all exposed here.
    """

    def __init__(
        self,
        fluent_connection,
        remote_file_handler: Optional[Any] = None,
    ):
        """Solver session.

        Args:
            fluent_connection (:ref:`ref_fluent_connection`): Encapsulates a Fluent connection.
            remote_file_handler: Supports file upload and download.
        """
        super(Solver, self).__init__(
            fluent_connection=fluent_connection, remote_file_handler=remote_file_handler
        )
        self._build_from_fluent_connection(fluent_connection)

    def _build_from_fluent_connection(self, fluent_connection):
        self._tui_service = self.datamodel_service_tui
        self._se_service = self.datamodel_service_se
        self._settings_service = self.settings_service
        self._tui = None
        self._workflow = None
        self._system_coupling = None
        self._settings_root = None
        self._version = None
        self._lck = threading.Lock()
        self.svar_service = self.fluent_connection.create_service(SVARService)
        self.svar_info = SVARInfo(self.svar_service)
        self._reduction_service = self.fluent_connection.create_service(
            ReductionService, self.error_state
        )
        if int(self.version) >= 241:
            self.reduction = Reduction(self._reduction_service)
        else:
            self.reduction = reduction_old

    def build_from_fluent_connection(self, fluent_connection):
        """Build a solver session object from fluent_connection object."""
        super(Solver, self).build_from_fluent_connection(fluent_connection)
        self._build_from_fluent_connection(fluent_connection)

    @property
    def svar_data(self) -> SVARData:
        """Return the SVARData handle."""
        try:
            return SVARData(self.svar_service, self.svar_info)
        except RuntimeError:
            return None

    @property
    def version(self):
        """Fluent's product version."""
        if self._version is None:
            self._version = get_version_for_file_name(session=self)
        return self._version

    @property
    def tui(self):
        """Instance of ``main_menu`` on which Fluent's SolverTUI methods can be
        executed."""
        if self._tui is None:
            try:
                tui_module = importlib.import_module(
                    f"ansys.fluent.core.solver.tui_{self.version}"
                )
                self._tui = tui_module.main_menu(
                    self._tui_service, self._version, "solver", []
                )
            except ImportError:
                tui_logger.warning(_CODEGEN_MSG_TUI)
                self._tui = TUIMenu(self._tui_service, self._version, "solver", [])
        return self._tui

    @property
    def _workflow_se(self):
        """Datamodel root for workflow."""
        try:
            workflow_module = importlib.import_module(
                f"ansys.fluent.core.datamodel_{self.version}.workflow"
            )
            workflow_se = workflow_module.Root(self._se_service, "workflow", [])
        except ImportError:
            datamodel_logger.warning(_CODEGEN_MSG_DATAMODEL)
            workflow_se = PyMenuGeneric(self._se_service, "workflow")
        return workflow_se

    @property
    def workflow(self):
        """Datamodel root for workflow."""
        if not self._workflow:
            self._workflow = WorkflowWrapper(self._workflow_se, Solver)
        return self._workflow

    @property
    def _root(self):
        """Root settings object."""
        if self._settings_root is None:
            self._settings_root = settings_get_root(
                flproxy=self._settings_service, version=self.version
            )
        return self._settings_root

    @property
    def system_coupling(self):
        if self._system_coupling is None:
            self._system_coupling = SystemCoupling(self)
        return self._system_coupling

    @property
    def file(self):
        """Settings for file."""
        return self._root.file

    @property
    def mesh(self):
        """Settings for mesh."""
        return self._root.mesh

    @property
    def setup(self):
        """Settings for setup."""
        return self._root.setup

    @property
    def solution(self):
        """Settings for solution."""
        return self._root.solution

    @property
    def results(self):
        """Settings for results."""
        return self._root.results

    @property
    def parametric_studies(self):
        """Settings for parametric_studies."""
        return self._root.parametric_studies

    @property
    def current_parametric_study(self):
        """Settings for current_parametric_study."""
        return self._root.current_parametric_study

    @property
    def parameters(self):
        """Settings for parameters."""
        return self._root.parameters

    @property
    def parallel(self):
        """Settings for parallel."""
        return self._root.parallel

    @property
    def report(self):
        """Settings for report."""
        return self._root.report

    @property
    def server(self):
        """Settings for server."""
        return self._root.server

    @property
    def preferences(self):
        """Datamodel root of preferences."""
        if self._preferences is None:
            self._preferences = _get_preferences(self)
        return self._preferences

    def _sync_from_future(self, fut: Future):
        with self._lck:
            try:
                fut_session = fut.result()
            except Exception as ex:
                raise RuntimeError("Unable to read mesh") from ex
            state = self._root.get_state()
            self.build_from_fluent_connection(fut_session.fluent_connection)
            # TODO temporary fix till set_state at settings root is fixed
            _set_state_safe(self._root, state)

    def read_case_lightweight(self, file_name: str):
        """Read a case file using light IO mode if ``pyfluent.USE_LIGHT_IO`` is set to
        ``True``.

        Parameters
        ----------
        file_name : str
            Case file name
        """
        import ansys.fluent.core as pyfluent

        self.file.read(file_type="case", file_name=file_name, lightweight_setup=True)
        launcher_args = dict(self.fluent_connection.launcher_args)
        launcher_args.pop("lightweight_mode", None)
        launcher_args["case_file_name"] = file_name
        fut: Future = asynchronous(pyfluent.launch_fluent)(**launcher_args)
        fut.add_done_callback(functools.partial(Solver._sync_from_future, self))

    def __call__(self):
        return self._root.get_state()

    def read_case(
        self,
        file_name: str,
    ):
        """Read a case file.

        Parameters
        ----------
        file_name : str
            Case file name
        """
        self._remote_file_handler.upload(
            file_name=file_name,
            on_uploaded=(lambda file_name: self.file.read_case(file_name=file_name)),
        )

    def write_case(
        self,
        file_name: str,
    ):
        """Write a case file.
        Parameters
        ----------
        file_name : str
            Case file name
        """
        self._remote_file_handler.download(
            file_name=file_name,
            before_downloaded=(
                lambda file_name: self.file.write_case(file_name=file_name)
            ),
        )
