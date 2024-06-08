import gc
from time import sleep

from google.protobuf.json_format import MessageToDict
import pytest
from util.meshing_workflow import new_mesh_session  # noqa: F401
from util.solver_workflow import new_solver_session  # noqa: F401

from ansys.api.fluent.v0 import datamodel_se_pb2
from ansys.api.fluent.v0.variant_pb2 import Variant
import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
from ansys.fluent.core.services.datamodel_se import (
    PyCommand,
    PyMenu,
    PyMenuGeneric,
    PyNamedObjectContainer,
    PyTextual,
    ReadOnlyObjectError,
    _convert_value_to_variant,
    _convert_variant_to_value,
    convert_path_to_se_path,
)
from ansys.fluent.core.streaming_services.datamodel_streaming import DatamodelStream
from ansys.fluent.core.utils.execution import timeout_loop


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, None),
        (False, False),
        (True, True),
        (1, 1),
        (1.0, 1.0),
        ("abc", "abc"),
        ((1, 2, 3), [1, 2, 3]),
        ([1, 2, 3], [1, 2, 3]),
        ({"a": 5}, {"a": 5}),
        ({"a": [1, 2, 3]}, {"a": [1, 2, 3]}),
        ({"a": {"b": 5}}, {"a": {"b": 5}}),
    ],
)
def test_convert_value_to_variant_to_value(value, expected):
    variant = Variant()
    _convert_value_to_variant(value, variant)
    assert expected == _convert_variant_to_value(variant)


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_event_subscription(new_mesh_session):
    session = new_mesh_session
    session.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    tags = [
        "/workflow/created/TaskObject",
        "/workflow/modified/TaskObject:TaskObject1/Arguments",
        "/workflow/deleted/TaskObject:TaskObject1",
        "/workflow/affected/TaskObject:TaskObject1",
        "/workflow/affected/TaskObject",
        "/workflow/attribute_changed/TaskObject:TaskObject1/TaskList/isActive",
        "/workflow/command_attribute_changed/InitializeWorkflow/arguments",
        "/workflow/command_executed/InitializeWorkflow",
    ]
    request = datamodel_se_pb2.SubscribeEventsRequest()
    e1 = request.eventrequest.add(rules="workflow")
    e1.createdEventRequest.parentpath = ""
    e1.createdEventRequest.childtype = "TaskObject"
    e2 = request.eventrequest.add(rules="workflow")
    e2.modifiedEventRequest.path = "TaskObject:TaskObject1/Arguments"
    e3 = request.eventrequest.add(rules="workflow")
    e3.deletedEventRequest.path = "TaskObject:TaskObject1"
    e4 = request.eventrequest.add(rules="workflow")
    e4.affectedEventRequest.path = "TaskObject:TaskObject1"
    e5 = request.eventrequest.add(rules="workflow")
    e5.affectedEventRequest.path = ""
    e5.affectedEventRequest.subtype = "TaskObject"
    e6 = request.eventrequest.add(rules="workflow")
    e6.attributeChangedEventRequest.path = "TaskObject:TaskObject1/TaskList"
    e6.attributeChangedEventRequest.attribute = "isActive"
    e7 = request.eventrequest.add(rules="workflow")
    e7.commandAttributeChangedEventRequest.path = ""
    e7.commandAttributeChangedEventRequest.command = "InitializeWorkflow"
    e7.commandAttributeChangedEventRequest.attribute = "arguments"
    e8 = request.eventrequest.add(rules="workflow")
    e8.commandExecutedEventRequest.path = ""
    e8.commandExecutedEventRequest.command = "InitializeWorkflow"
    response = session._datamodel_service_se.subscribe_events(MessageToDict(request))
    assert all(
        [
            r["status"] == datamodel_se_pb2.STATUS_SUBSCRIBED and r["tag"] == t
            for r, t in zip(response, tags)
        ]
    )
    response = session._datamodel_service_se.unsubscribe_events(tags)
    assert all(
        [
            r["status"] == datamodel_se_pb2.STATUS_UNSUBSCRIBED and r["tag"] == t
            for r, t in zip(response, tags)
        ]
    )


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_add_on_child_created(new_mesh_session):
    meshing = new_mesh_session
    child_paths = []
    subscription = meshing.workflow.add_on_child_created(
        "TaskObject", lambda obj: child_paths.append(convert_path_to_se_path(obj.path))
    )
    assert child_paths == []
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    sleep(5)
    assert len(child_paths) > 0
    child_paths.clear()
    subscription.unsubscribe()
    meshing.workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")
    sleep(5)
    assert child_paths == []


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_add_on_deleted(new_mesh_session):
    meshing = new_mesh_session
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    data = []
    subscription = meshing.workflow.TaskObject["Import Geometry"].add_on_deleted(
        lambda obj: data.append(convert_path_to_se_path(obj.path))
    )
    assert data == []
    meshing.workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")
    sleep(5)
    assert len(data) > 0


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_add_on_changed(new_mesh_session):
    meshing = new_mesh_session
    task_list = meshing.workflow.Workflow.TaskList
    assert isinstance(task_list(), list)
    assert len(task_list()) == 0
    data = []
    subscription = task_list.add_on_changed(lambda obj: data.append(len(obj())))
    assert data == []
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    sleep(5)
    assert len(data) > 0
    assert data[-1] > 0
    data.clear()
    subscription.unsubscribe()
    meshing.workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")
    sleep(5)
    assert data == []


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_add_on_affected(new_mesh_session):
    meshing = new_mesh_session
    data = []
    subscription = meshing.workflow.Workflow.add_on_affected(
        lambda obj: data.append(True)
    )
    assert data == []
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    sleep(5)
    assert len(data) > 0
    assert data[0] == True

    calls = []
    subscription2 = meshing.workflow.add_on_affected(lambda obj: calls.append(True))
    geom = examples.download_file(
        file_name="mixing_elbow.pmdb", directory="pyfluent/mixing_elbow"
    )
    import_geom = meshing.workflow.TaskObject["Import Geometry"]
    assert "FileName" not in import_geom.Arguments()
    assert import_geom.command_arguments()["FileName"] is None
    import_geom.Arguments = {"FileName": geom}
    assert import_geom.Arguments()["FileName"] == geom
    assert import_geom.command_arguments()["FileName"] == geom
    sleep(1)
    assert calls == [True]
    import_geom.Arguments = {"FileName": "dummy"}
    sleep(1)
    assert calls == 2 * [True]
    import_geom.Arguments = {"FileName": geom}
    sleep(1)
    assert calls == 3 * [True]
    execute_state = [meshing.workflow()]
    import_geom.Execute()
    calls_after_execute = []
    loop_count = 10
    for i in range(loop_count):
        sleep(5)
        calls_after_execute.append(list(calls))
        execute_state.append(meshing.workflow())
    assert all(state == execute_state[1] for state in execute_state[2:])
    call_count = sum(map(len, calls_after_execute))
    assert call_count == 6 * loop_count
    assert calls_after_execute == loop_count * [6 * [True]]
    subscription2.unsubscribe()

    data.clear()
    subscription.unsubscribe()
    meshing.workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")
    sleep(5)
    assert data == []


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_add_on_affected_at_type_path(new_mesh_session):
    meshing = new_mesh_session
    data = []
    subscription = meshing.workflow.add_on_affected_at_type_path(
        "TaskObject", lambda obj: data.append(True)
    )
    assert data == []
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    sleep(5)
    assert len(data) > 0
    assert data[0] == True
    data.clear()
    subscription.unsubscribe()
    meshing.workflow.InitializeWorkflow(WorkflowType="Fault-tolerant Meshing")
    sleep(5)
    assert data == []


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_add_on_command_executed(new_mesh_session):
    meshing = new_mesh_session
    data = []
    subscription = meshing.meshing.add_on_command_executed(
        "ImportGeometry", lambda obj, command, args: data.append(True)
    )
    assert data == []
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    import_file_name = examples.download_file(
        "mixing_elbow.pmdb", "pyfluent/mixing_elbow"
    )
    meshing.meshing.ImportGeometry(FileName=import_file_name)
    sleep(5)
    assert len(data) > 0
    assert data[0] == True
    data.clear()
    subscription.unsubscribe()
    meshing.meshing.ImportGeometry(FileName=import_file_name)
    sleep(5)
    assert data == []


@pytest.fixture
def disable_datamodel_cache(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(pyfluent, "DATAMODEL_USE_STATE_CACHE", False)


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_datamodel_streaming_full_diff_state(disable_datamodel_cache, new_mesh_session):
    meshing = new_mesh_session
    datamodel_service_se = meshing._datamodel_service_se
    stream = DatamodelStream(datamodel_service_se)
    stream.start(rules="meshing", no_commands_diff_state=False)

    def cb(state, deleted_paths):
        if state:
            state = _convert_variant_to_value(state)
        cb.states.append(state)

    cb.states = []

    stream.register_callback(cb)

    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    import_file_name = examples.download_file(
        "mixing_elbow.pmdb", "pyfluent/mixing_elbow"
    )
    meshing.meshing.ImportGeometry(FileName=import_file_name)
    sleep(5)
    assert "ImportGeometry:ImportGeometry1" in (y for x in cb.states for y in x)


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_datamodel_streaming_no_commands_diff_state(
    disable_datamodel_cache, new_mesh_session
):
    meshing = new_mesh_session
    datamodel_service_se = meshing._datamodel_service_se
    stream = DatamodelStream(datamodel_service_se)
    stream.start(rules="meshing", no_commands_diff_state=True)

    def cb(state, deleted_paths):
        if state:
            state = _convert_variant_to_value(state)
        cb.states.append(state)

    cb.states = []

    stream.register_callback(cb)

    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    import_file_name = examples.download_file(
        "mixing_elbow.pmdb", "pyfluent/mixing_elbow"
    )
    meshing.meshing.ImportGeometry(FileName=import_file_name)
    sleep(5)
    assert "ImportGeometry:ImportGeometry1" not in (y for x in cb.states for y in x)


@pytest.mark.fluent_version(">=24.2")
@pytest.mark.codegen_required
def test_get_object_names_wtm(new_mesh_session):
    meshing = new_mesh_session

    assert not meshing.workflow.TaskObject.get_object_names()

    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

    child_object_names = [
        "Import Geometry",
        "Add Local Sizing",
        "Generate the Surface Mesh",
        "Describe Geometry",
        "Apply Share Topology",
        "Enclose Fluid Regions (Capping)",
        "Update Boundaries",
        "Create Regions",
        "Update Regions",
        "Add Boundary Layers",
        "Generate the Volume Mesh",
    ]

    assert meshing.workflow.TaskObject.get_object_names() == child_object_names


@pytest.mark.fluent_version(">=23.2")
@pytest.mark.codegen_required
def test_get_and_set_state_for_command_arg_instance(new_mesh_session):
    meshing = new_mesh_session

    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

    x = meshing.meshing.ImportGeometry.create_instance()

    assert x.LengthUnit() == "mm"

    assert x.LengthUnit.allowed_values() == ["m", "cm", "mm", "in", "ft", "um", "nm"]

    x.LengthUnit.set_state("ft")

    assert x.LengthUnit.get_state() == "ft"

    assert x.CadImportOptions.ExtractFeatures()

    x.CadImportOptions.ExtractFeatures.set_state(False)

    assert not x.CadImportOptions.ExtractFeatures()

    x.set_state({"FileName": "dummy_file_name.dummy_extn"})

    assert x.FileName() == "dummy_file_name.dummy_extn"


def _is_internal_name(name: str, prefix: str) -> bool:
    return name.startswith(prefix) and name.removeprefix(prefix).isdigit()


@pytest.mark.codegen_required
def test_task_object_keys_are_display_names(new_mesh_session):
    meshing = new_mesh_session
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    task_object_state = meshing.workflow.TaskObject()
    assert len(task_object_state) > 0
    assert not any(_is_internal_name(x, "TaskObject:") for x in task_object_state)


def test_generic_datamodel(new_solver_session):
    solver = new_solver_session
    solver.scheme_eval.scheme_eval("(init-flserver)")
    flserver = PyMenuGeneric(solver._datamodel_service_se, "flserver")
    assert flserver.Case.Solution.Calculation.TimeStepSize() == 1.0


@pytest.mark.fluent_version(">=24.2")
def test_named_object_specific_methods_using_flserver(new_solver_session):
    import_file_name = examples.download_file(
        "mixing_elbow.cas.h5", "pyfluent/mixing_elbow"
    )
    solver = new_solver_session
    solver.file.read(file_type="case", file_name=import_file_name)
    solver.solution.initialization.hybrid_initialize()
    solver.solution.run_calculation.iterate(iter_count=10)
    solver.tui.display.objects.create(
        "contour",
        "contour-z1",
        "field",
        "velocity-magnitude",
        "surfaces-list",
        "cold-inlet",
    )
    solver.tui.display.objects.create(
        "contour",
        "contour-z2",
        "field",
        "velocity-magnitude",
        "surfaces-list",
        "hot-inlet",
    )
    solver.tui.display.objects.create(
        "contour",
        "contour-z3",
        "field",
        "velocity-magnitude",
        "surfaces-list",
        "outlet",
    )
    solver.tui.display.objects.create(
        "contour",
        "contour-z4",
        "field",
        "velocity-magnitude",
        "surfaces-list",
        "wall-elbow",
    )
    solver.tui.display.objects.create(
        "contour",
        "contour-z5",
        "field",
        "velocity-magnitude",
        "surfaces-list",
        "wall-inlet",
    )

    flserver = PyMenuGeneric(solver._datamodel_service_se, "flserver")

    assert set(flserver.Case.Results.Graphics.Contour.get_object_names()) == {
        "contour-z1",
        "contour-z2",
        "contour-z3",
        "contour-z4",
        "contour-z5",
    }

    assert "contour-x1" not in flserver.Case.Results.Graphics.Contour.get_object_names()

    flserver.Case.Results.Graphics.Contour["contour-z1"].rename("contour-x1")

    assert "contour-x1" in flserver.Case.Results.Graphics.Contour.get_object_names()

    flserver.Case.Results.Graphics.delete_child_objects(
        "Contour", ["contour-x1", "contour-z2"]
    )

    assert set(flserver.Case.Results.Graphics.Contour.get_object_names()) == {
        "contour-z3",
        "contour-z4",
        "contour-z5",
    }

    flserver.Case.Results.Graphics.delete_all_child_objects("Contour")

    assert not flserver.Case.Results.Graphics.Contour.get_object_names()


@pytest.mark.fluent_version(">=24.2")
def test_named_object_specific_methods(new_mesh_session):
    meshing = new_mesh_session
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

    assert set(meshing.workflow.TaskObject.get_object_names()) == {
        "Import Geometry",
        "Add Local Sizing",
        "Generate the Surface Mesh",
        "Describe Geometry",
        "Apply Share Topology",
        "Enclose Fluid Regions (Capping)",
        "Update Boundaries",
        "Create Regions",
        "Update Regions",
        "Add Boundary Layers",
        "Generate the Volume Mesh",
    }

    assert "xyz" not in meshing.workflow.TaskObject.get_object_names()

    meshing.workflow.TaskObject["Import Geometry"].rename("xyz")

    assert "xyz" in meshing.workflow.TaskObject.get_object_names()

    meshing.workflow.delete_all_child_objects("TaskObject")

    assert not meshing.workflow.TaskObject.get_object_names()


@pytest.mark.codegen_required
@pytest.mark.fluent_version(">=24.1")
def test_command_creation_inside_singleton(new_mesh_session):
    meshing = new_mesh_session
    read_mesh = meshing.meshing.File.ReadMesh.create_instance()
    assert read_mesh.FileName is not None


@pytest.mark.codegen_required
def test_read_ony_set_state(new_mesh_session):
    meshing = new_mesh_session
    meshing.preferences.MeshingWorkflow.SaveCheckpointFiles = True
    assert meshing.preferences.MeshingWorkflow.CheckpointingOption.is_read_only()
    with pytest.raises(ReadOnlyObjectError):
        meshing.preferences.MeshingWorkflow.CheckpointingOption = "Write into memory"

    assert "set_state" not in dir(
        meshing.preferences.MeshingWorkflow.CheckpointingOption
    )


test_rules = (
    "RULES:\n"
    "    SINGLETON: ROOT\n"
    "        members = A\n"
    "        OBJECT: A\n"
    "            members = B, X\n"
    "            commands = C\n"
    "            isABC = $./X == ABC\n"
    "            OBJECT: B\n"
    "            END\n"
    "            STRING: X\n"
    "                default = IJK\n"
    "            END\n"
    "            COMMAND: C\n"
    "                returnType = Logical\n"
    "                functionName = S_C\n"
    "                isABC = $../X == ABC\n"
    "            END\n"
    "        END\n"
    "     END\n"
    "END\n"
)


class test_root(PyMenu):
    def __init__(self, service, rules, path):
        self.A = self.__class__.A(service, rules, path + [("A", "")])
        super().__init__(service, rules, path)

    class A(PyNamedObjectContainer):
        class _A(PyMenu):
            def __init__(self, service, rules, path):
                self.B = self.__class__.B(service, rules, path + [("B", "")])
                self.X = self.__class__.X(service, rules, path + [("X", "")])
                self.C = self.__class__.C(service, rules, "C", path)
                super().__init__(service, rules, path)

            class B(PyNamedObjectContainer):
                class _B(PyMenu):
                    pass

            class X(PyTextual):
                pass

            class C(PyCommand):
                pass


def _create_datamodel_root(session, rules_str) -> PyMenu:
    rules_file_name = "test.fdl"
    session.scheme_eval.scheme_eval(
        f'(with-output-to-file "{rules_file_name}" (lambda () (format "~a" "{rules_str}")))'
    )
    session.scheme_eval.scheme_eval(
        '(state/register-new-state-engine "test" "test.fdl")'
    )
    session.scheme_eval.scheme_eval(f'(remove-file "{rules_file_name}")')
    assert session.scheme_eval.scheme_eval('(state/find-root "test")') > 0
    return test_root(session._se_service, "test", [])


@pytest.mark.fluent_version(">=24.2")
def test_on_child_created_lifetime(new_solver_session):
    solver = new_solver_session
    root = _create_datamodel_root(solver, test_rules)
    root.A["A1"] = {}
    data = []
    h = root.A["A1"].add_on_child_created("B", lambda _: data.append(1))
    root.A["A1"].add_on_child_created("B", lambda _: data.append(2))
    gc.collect()
    assert "/test/created/A:A1/B" in solver._se_service.subscriptions
    assert "/test/created/A:A1/B-1" in solver._se_service.subscriptions
    root.A["A1"].B["B1"] = {}
    assert timeout_loop(lambda: data == [1, 2], 5)
    del root.A["A1"]
    assert "/test/created/A:A1/B" not in solver._se_service.subscriptions
    assert "/test/created/A:A1/B-1" not in solver._se_service.subscriptions


@pytest.mark.fluent_version(">=24.2")
def test_on_deleted_lifetime(new_solver_session):
    solver = new_solver_session
    root = _create_datamodel_root(solver, test_rules)
    root.A["A1"] = {}
    data = []
    h = root.A["A1"].add_on_deleted(lambda _: data.append(1))
    root.A["A1"].add_on_deleted(lambda _: data.append(2))
    gc.collect()
    assert "/test/deleted/A:A1" in solver._se_service.subscriptions
    assert "/test/deleted/A:A1-1" in solver._se_service.subscriptions
    del root.A["A1"]
    assert timeout_loop(lambda: data == [1, 2], 5)
    assert timeout_loop(
        lambda: "/test/deleted/A:A1" not in solver._se_service.subscriptions, 5
    )
    assert timeout_loop(
        lambda: "/test/deleted/A:A1-1" not in solver._se_service.subscriptions, 5
    )


@pytest.mark.fluent_version(">=24.2")
def test_on_changed_lifetime(new_solver_session):
    solver = new_solver_session
    root = _create_datamodel_root(solver, test_rules)
    root.A["A1"] = {}
    data = []
    h = root.A["A1"].X.add_on_changed(lambda _: data.append(1))
    root.A["A1"].X.add_on_changed(lambda _: data.append(2))
    gc.collect()
    assert "/test/modified/A:A1/X" in solver._se_service.subscriptions
    assert "/test/modified/A:A1/X-1" in solver._se_service.subscriptions
    root.A["A1"].X = "ABC"
    assert timeout_loop(lambda: data == [1, 2], 5)
    del root.A["A1"]
    assert "/test/modified/A:A1/X" not in solver._se_service.subscriptions
    assert "/test/modified/A:A1/X-1" not in solver._se_service.subscriptions


@pytest.mark.fluent_version(">=24.2")
def test_on_affected_lifetime(new_solver_session):
    solver = new_solver_session
    root = _create_datamodel_root(solver, test_rules)
    root.A["A1"] = {}
    data = []
    h = root.A["A1"].add_on_affected(lambda _: data.append(1))
    root.A["A1"].add_on_affected(lambda _: data.append(2))
    gc.collect()
    assert "/test/affected/A:A1" in solver._se_service.subscriptions
    assert "/test/affected/A:A1-1" in solver._se_service.subscriptions
    root.A["A1"].X = "ABC"
    assert timeout_loop(lambda: data == [1, 2], 5)
    del root.A["A1"]
    assert "/test/affected/A:A1" not in solver._se_service.subscriptions
    assert "/test/affected/A:A1-1" not in solver._se_service.subscriptions


@pytest.mark.fluent_version(">=24.2")
def test_on_affected_at_type_path_lifetime(new_solver_session):
    solver = new_solver_session
    root = _create_datamodel_root(solver, test_rules)
    root.A["A1"] = {}
    data = []
    h = root.A["A1"].add_on_affected_at_type_path("B", lambda _: data.append(1))
    root.A["A1"].add_on_affected_at_type_path("B", lambda _: data.append(2))
    gc.collect()
    assert "/test/affected/A:A1/B" in solver._se_service.subscriptions
    assert "/test/affected/A:A1/B-1" in solver._se_service.subscriptions
    root.A["A1"].B["B1"] = {}
    assert timeout_loop(lambda: data == [1, 2], 5)
    del root.A["A1"]
    assert "/test/affected/A:A1/B" not in solver._se_service.subscriptions
    assert "/test/affected/A:A1/B-1" not in solver._se_service.subscriptions


@pytest.mark.fluent_version(">=24.2")
def test_on_command_executed_lifetime(new_solver_session):
    solver = new_solver_session
    root = _create_datamodel_root(solver, test_rules)
    root.A["A1"] = {}
    data = []
    h = root.A["A1"].add_on_command_executed("C", lambda *args: data.append(1))
    root.A["A1"].add_on_command_executed("C", lambda *args: data.append(2))
    gc.collect()
    assert "/test/command_executed/A:A1/C" in solver._se_service.subscriptions
    assert "/test/command_executed/A:A1/C-1" in solver._se_service.subscriptions
    root.A["A1"].C()
    assert timeout_loop(lambda: data == [1, 2], 5)
    del root.A["A1"]
    assert "/test/command_executed/A:A1/C" not in solver._se_service.subscriptions
    assert "/test/command_executed/A:A1/C-1" not in solver._se_service.subscriptions


@pytest.mark.fluent_version(">=24.2")
def test_on_attribute_changed_lifetime(new_solver_session):
    solver = new_solver_session
    root = _create_datamodel_root(solver, test_rules)
    root.A["A1"] = {}
    data = []
    h = root.A["A1"].add_on_attribute_changed("isABC", lambda _: data.append(1))
    root.A["A1"].add_on_attribute_changed("isABC", lambda _: data.append(2))
    gc.collect()
    assert "/test/attribute_changed/A:A1/isABC" in solver._se_service.subscriptions
    assert "/test/attribute_changed/A:A1/isABC-1" in solver._se_service.subscriptions
    root.A["A1"].X = "ABC"
    assert timeout_loop(lambda: data == [1, 2], 5)
    del root.A["A1"]
    assert "/test/attribute_changed/A:A1/isABC" not in solver._se_service.subscriptions
    assert (
        "/test/attribute_changed/A:A1/isABC-1" not in solver._se_service.subscriptions
    )


@pytest.mark.fluent_version(">=24.2")
def test_on_command_attribute_changed_lifetime(new_solver_session):
    solver = new_solver_session
    root = _create_datamodel_root(solver, test_rules)
    root.A["A1"] = {}
    data = []
    h = root.A["A1"].add_on_command_attribute_changed(
        "C", "isABC", lambda _: data.append(1)
    )
    root.A["A1"].add_on_command_attribute_changed(
        "C", "isABC", lambda _: data.append(2)
    )
    gc.collect()
    assert (
        "/test/command_attribute_changed/A:A1/C/isABC"
        in solver._se_service.subscriptions
    )
    assert (
        "/test/command_attribute_changed/A:A1/C/isABC-1"
        in solver._se_service.subscriptions
    )
    root.A["A1"].X = "ABC"
    assert timeout_loop(lambda: data == [1, 2], 5)
    del root.A["A1"]
    assert (
        "/test/command_attribute_changed/A:A1/C/isABC"
        not in solver._se_service.subscriptions
    )
    assert (
        "/test/command_attribute_changed/A:A1/C/isABC-1"
        not in solver._se_service.subscriptions
    )


@pytest.mark.fluent_version(">=24.2")
def test_on_affected_lifetime_with_delete_child_objects(new_solver_session):
    solver = new_solver_session
    root = _create_datamodel_root(solver, test_rules)
    pyfluent.logging.enable()
    root.A["A1"] = {}
    data = []
    h = root.A["A1"].add_on_affected(lambda _: data.append(1))
    root.A["A1"].add_on_affected(lambda _: data.append(2))
    gc.collect()
    assert "/test/affected/A:A1" in solver._se_service.subscriptions
    assert "/test/affected/A:A1-1" in solver._se_service.subscriptions
    root.A["A1"].X = "ABC"
    assert timeout_loop(lambda: data == [1, 2], 5)
    root.delete_child_objects("A", ["A1"])
    assert "/test/affected/A:A1" not in solver._se_service.subscriptions
    assert "/test/affected/A:A1-1" not in solver._se_service.subscriptions


@pytest.mark.fluent_version(">=24.2")
def test_on_affected_lifetime_with_delete_all_child_objects(new_solver_session):
    solver = new_solver_session
    root = _create_datamodel_root(solver, test_rules)
    pyfluent.logging.enable()
    root.A["A1"] = {}
    data = []
    h = root.A["A1"].add_on_affected(lambda _: data.append(1))
    root.A["A1"].add_on_affected(lambda _: data.append(2))
    gc.collect()
    assert "/test/affected/A:A1" in solver._se_service.subscriptions
    assert "/test/affected/A:A1-1" in solver._se_service.subscriptions
    root.A["A1"].X = "ABC"
    assert timeout_loop(lambda: data == [1, 2], 5)
    root.delete_all_child_objects("A")
    assert "/test/affected/A:A1" not in solver._se_service.subscriptions
    assert "/test/affected/A:A1-1" not in solver._se_service.subscriptions
