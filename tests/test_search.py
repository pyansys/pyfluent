import pytest
from util.fixture_fluent import load_static_mixer_case  # noqa: F401
from util.meshing_workflow import new_watertight_workflow_session  # noqa: F401
from util.solver_workflow import new_solver_session  # noqa: F401

import ansys.fluent.core as pyfluent
from ansys.fluent.core.utils.search import _get_version_path_prefix_from_obj


@pytest.mark.codegen_required
def test_exact_search(capsys):
    pyfluent.search("font", exact=True)
    lines = capsys.readouterr().out.splitlines()
    assert "Font" not in lines
    assert "<solver_session>.tui.preferences.appearance.charts.font (Object)" in lines


@pytest.mark.codegen_required
def test_match_case_search(capsys):
    pyfluent.search("Font")
    lines = capsys.readouterr().out.splitlines()
    assert "<solver_session>.tui.preferences.appearance.charts.font (Object)" in lines
    assert "<solver_session>.preferences.Appearance.Charts.Font (Object)" in lines


@pytest.mark.codegen_required
def test_misspelled_search(capsys):
    pyfluent.search("cfb_lma")
    lines = capsys.readouterr().out.splitlines()
    assert (
        "<solver_session>.setup.models.viscous.geko_options.cbf_lam (Parameter)"
        in lines
    )


@pytest.mark.codegen_required
def test_wildcard_search(capsys):
    pyfluent.search("iter*", wildcard=True)
    lines = capsys.readouterr().out.splitlines()
    assert "<solver_session>.solution.run_calculation.iter_count (Parameter)" in lines
    assert "<solver_session>.solution.run_calculation.iterating (Query)" in lines


@pytest.mark.codegen_required
def test_chinese_semantic_search(capsys):
    pyfluent.search("读", language="cmn")
    lines = capsys.readouterr().out.splitlines()
    assert "<solver_session>.file.read_case (Command)" in lines
    assert "<meshing_session>.meshing.File.ReadMesh (Command)" in lines

    pyfluent.search("写", language="cmn")
    lines = capsys.readouterr().out.splitlines()
    assert "<solver_session>.file.write_case (Command)" in lines
    assert "<meshing_session>.meshing.File.WriteMesh (Command)" in lines


@pytest.mark.codegen_required
def test_japanese_semantic_search(capsys):
    pyfluent.search("フォント", language="jpn")
    lines = capsys.readouterr().out.splitlines()
    assert "<solver_session>.tui.preferences.appearance.charts.font (Object)" in lines
    assert "<solver_session>.preferences.Appearance.Charts.Font (Object)" in lines


@pytest.mark.codegen_required
def test_search(capsys):
    pyfluent._search("display")
    lines = capsys.readouterr().out.splitlines()
    assert "<meshing_session>.tui.display (Object)" in lines
    assert "<meshing_session>.tui.display.update_scene.display (Command)" in lines
    assert (
        "<meshing_session>.preferences.Graphics.MeshingMode.GraphicsWindowDisplayTimeout (Parameter)"
        in lines
    )
    assert '<solver_session>.results.graphics.mesh["<name>"].display (Command)' in lines
    assert (
        '<solver_session>.results.graphics.mesh["<name>"].display_state_name (Parameter)'
        in lines
    )

    pyfluent._search("display", match_whole_word=True)
    lines = capsys.readouterr().out.splitlines()
    assert '<solver_session>.results.graphics.mesh["<name>"].display (Command)' in lines
    assert (
        '<solver_session>.results.graphics.mesh["<name>"].display_state_name (Parameter)'
        not in lines
    )

    pyfluent._search("Display", match_case=True)
    lines = capsys.readouterr().out.splitlines()
    assert "<meshing_session>.tui.display (Object)" not in lines
    assert (
        "<meshing_session>.preferences.Graphics.MeshingMode.GraphicsWindowDisplayTimeout (Parameter)"
        in lines
    )

    pyfluent._search(
        "GraphicsWindowDisplayTimeout", match_whole_word=True, match_case=True
    )
    lines = capsys.readouterr().out.splitlines()
    assert (
        "<meshing_session>.preferences.Graphics.MeshingMode.GraphicsWindowDisplayTimeout (Parameter)"
        in lines
    )
    assert (
        "<solver_session>.preferences.Graphics.MeshingMode.GraphicsWindowDisplayTimeoutValue (Parameter)"
        not in lines
    )


@pytest.mark.codegen_required
@pytest.mark.fluent_version("latest")
def test_get_version_path_prefix_from_obj(
    new_watertight_workflow_session, new_solver_session
):
    meshing = new_watertight_workflow_session
    solver = new_solver_session
    version = solver._version
    assert _get_version_path_prefix_from_obj(meshing) == (
        version,
        ["<meshing_session>"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(solver) == (
        version,
        ["<solver_session>"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(meshing.tui.file.import_) == (
        version,
        ["<meshing_session>", "tui", "file", "import_"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(meshing.tui.file.read_case) == (
        None,
        None,
        None,
    )
    assert _get_version_path_prefix_from_obj(meshing.meshing) == (
        version,
        ["<meshing_session>", "meshing"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(meshing.workflow) == (
        version,
        ["<meshing_session>", "workflow"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(solver.workflow) == (
        version,
        ["<meshing_session>", "workflow"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(meshing.workflow.TaskObject) == (
        version,
        ["<meshing_session>", "workflow", "TaskObject:<name>"],
        '<search_root>["<name>"]',
    )
    assert _get_version_path_prefix_from_obj(
        meshing.workflow.TaskObject["Import Geometry"]
    ) == (
        version,
        ["<meshing_session>", "workflow", "TaskObject:<name>"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(meshing.preferences.Appearance.Charts) == (
        version,
        ["<solver_session>", "preferences", "Appearance", "Charts"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(solver.setup.models) == (
        version,
        ["<solver_session>"],
        "<search_root>",
    )
    assert _get_version_path_prefix_from_obj(solver.file.cff_files) == (
        None,
        None,
        None,
    )


@pytest.mark.codegen_required
@pytest.mark.fluent_version("latest")
def test_search_from_root(capsys, new_watertight_workflow_session):
    meshing = new_watertight_workflow_session
    pyfluent._search("display", search_root=meshing)
    lines = capsys.readouterr().out.splitlines()
    assert "<search_root>.tui.display (Object)" in lines
    pyfluent._search("display", search_root=meshing.tui)
    lines = capsys.readouterr().out.splitlines()
    assert "<search_root>.display (Object)" in lines
    pyfluent._search("display", search_root=meshing.tui.display)
    lines = capsys.readouterr().out.splitlines()
    assert "<search_root>.update_scene.display (Command)" in lines
    assert "<search_root>.display_states (Object)" in lines
    pyfluent._search("cad", search_root=meshing.meshing)
    lines = capsys.readouterr().out.splitlines()
    assert "<search_root>.GlobalSettings.EnableCleanCAD (Parameter)" in lines
    assert "<search_root>.LoadCADGeometry (Command)" in lines
    pyfluent._search("next", search_root=meshing.workflow)
    lines = capsys.readouterr().out.splitlines()
    assert '<search_root>.TaskObject["<name>"].InsertNextTask (Command)' in lines
    pyfluent._search("next", search_root=meshing.workflow.TaskObject)
    lines = capsys.readouterr().out.splitlines()
    assert '<search_root>["<name>"].InsertNextTask (Command)' in lines
    pyfluent._search("next", search_root=meshing.workflow.TaskObject["Import Geometry"])
    lines = capsys.readouterr().out.splitlines()
    assert "<search_root>.InsertNextTask (Command)" in lines
    pyfluent._search("timeout", search_root=meshing.preferences)
    lines = capsys.readouterr().out.splitlines()
    assert "<search_root>.General.IdleTimeout (Parameter)" in lines
    pyfluent._search("timeout", search_root=meshing.preferences.General)
    lines = capsys.readouterr().out.splitlines()
    assert "<search_root>.IdleTimeout (Parameter)" in lines


@pytest.mark.codegen_required
@pytest.mark.fluent_version("==23.2")
def test_search_settings_from_root(capsys, load_static_mixer_settings_only):
    solver = load_static_mixer_settings_only
    pyfluent._search("conduction", search_root=solver)
    lines = capsys.readouterr().out.splitlines()
    assert "<search_root>.tui.define.models.shell_conduction (Object)" in lines
    assert (
        '<search_root>.setup.boundary_conditions.wall["<name>"].phase["<name>"].shell_conduction["<name>"] (Object)'
        in lines
    )
    pyfluent._search("conduction", search_root=solver.setup.boundary_conditions)
    lines = capsys.readouterr().out.splitlines()
    assert (
        '<search_root>.wall["<name>"].phase["<name>"].shell_conduction["<name>"] (Object)'
        in lines
    )
    pyfluent._search("conduction", search_root=solver.setup.boundary_conditions.wall)
    lines = capsys.readouterr().out.splitlines()
    assert (
        '<search_root>["<name>"].phase["<name>"].shell_conduction["<name>"] (Object)'
        in lines
    )
    pyfluent._search(
        "conduction", search_root=solver.setup.boundary_conditions.wall["wall"]
    )
    lines = capsys.readouterr().out.splitlines()
    assert '<search_root>.phase["<name>"].shell_conduction["<name>"] (Object)' in lines
    pyfluent._search(
        "conduction", search_root=solver.setup.boundary_conditions.wall["wall"].phase
    )
    lines = capsys.readouterr().out.splitlines()
    assert '<search_root>["<name>"].shell_conduction["<name>"] (Object)' in lines
