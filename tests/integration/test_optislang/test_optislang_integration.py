from collections import OrderedDict
import os
from pathlib import Path
import shutil
import tempfile

import pytest

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
from ansys.fluent.core.filereader.case_file import CaseFile
from ansys.fluent.core.utils.fluent_version import FluentVersion


@pytest.mark.nightly
@pytest.mark.codegen_required
@pytest.mark.fluent_version("latest")
def test_simple_solve(mixing_elbow_param_case_data_session):
    """Use case 1: This optiSLang integration test performs these steps.

    - Reads a case file with and without data file
    - Gets input and output parameters and creates dictionary
    - Sets a variation on input parameters
    - Solve
    - Reread data

    This test queries the following using PyTest:
    - Session health
    - Input parameters
    - Output parameters
    """
    # Step 1: Launch fluent session and read case file with and without data file
    solver_session = mixing_elbow_param_case_data_session
    assert solver_session.health_check.is_serving
    case_path = examples.path("elbow_param.cas.h5")
    solver_session.settings.file.read_case_data(file_name=case_path)

    # Step 2: Get input and output parameters and create a dictionary
    reader = CaseFile(case_file_name=case_path)

    input_parameters = {}
    for p in reader.input_parameters():
        input_parameters[p.name] = (p.value, p.numeric_value, p.units)
    output_parameters = {}
    for o in reader.output_parameters():
        output_parameters[o.name] = (0, o.units)
    solver_session.settings.file.read_case(file_name=case_path)

    input_parameters = input_parameters["inlet2_temp"]
    output_parameters = output_parameters["outlet_temp-op"]

    # Step 3: Set a variation on these input parameters
    # variations/designs are generated by optiSLang based on
    # algorithm selected
    inputs_table = solver_session.settings.parameters.input_parameters.expression[
        "inlet2_temp"
    ] = {"value": 600}

    Path(pyfluent.EXAMPLES_PATH).mkdir(parents=True, exist_ok=True)
    tmp_save_path = tempfile.mkdtemp(dir=pyfluent.EXAMPLES_PATH)
    design_elbow_param_path = Path(tmp_save_path) / "design_elbow_param.cas.h5"
    solver_session.settings.file.write_case(file_name=str(design_elbow_param_path))

    assert design_elbow_param_path.exists()

    # Step 4: Solve
    solver_session.settings.solution.initialization.standard_initialize()

    # check if solution is steady or transient
    workflow = solver_session.rp_vars("rp-unsteady?")

    # iterate workflow
    if workflow:
        solver_session.settings.solution.run_calculation.dual_time_iterate()
    else:
        solver_session.settings.solution.run_calculation.iterate()

    convergence = solver_session.rp_vars("solution/converged?")

    # solution output (test conditional statement)
    if not convergence:  # -> let user know
        print("Failed to converge")
    else:
        print("Solution is converged")

    assert convergence == True, "Solution failed to converge"

    # Step 5: Read the data again from the case and data file
    solver_session.settings.file.read_case_data(file_name=case_path)

    inputs_table = solver_session.settings.parameters.input_parameters.expression[
        "inlet2_temp"
    ]()
    assert input_parameters[0] == "500 [K]"
    assert inputs_table["value"] == 500.0

    fluent_output_table = solver_session.settings.parameters.output_parameters.list()
    for key, entry in fluent_output_table.items():
        output_value = entry[0]
        output_unit = entry[1]

    assert output_value == 322.3360076327905

    # output_unit should assert the unit string but it doesn't currently
    # A bug has been submitted to address this
    assert output_unit == ["temperature", False]
    assert output_parameters[1] == "K"

    solver_session.exit()


@pytest.mark.nightly
@pytest.mark.codegen_required
@pytest.mark.fluent_version("latest")
def test_generate_read_mesh(mixing_elbow_geometry_filename):
    """Use case 2: This optiSLang integration test performs these steps.

    - Launch Fluent in Meshing Mode
    - Generate mesh with default workflow settings
    - Read created mesh file
    - Switch to solution and write case file

    This test queries the following using PyTest:
    - Session health
    """
    # Step 1: Launch fluent session in meshing mode
    meshing = pyfluent.launch_fluent(
        mode="meshing", precision="double", processor_count=2
    )
    assert meshing.health_check.is_serving
    temporary_resource_path = os.path.join(
        pyfluent.EXAMPLES_PATH, "test_generate_read_mesh_resources"
    )
    if os.path.exists(temporary_resource_path):
        shutil.rmtree(temporary_resource_path, ignore_errors=True)
    if not os.path.exists(temporary_resource_path):
        os.mkdir(temporary_resource_path)

    # Step 2: Generate mesh from geometry with default workflow settings
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    geo_import = meshing.workflow.TaskObject["Import Geometry"]
    geo_import.Arguments = dict(FileName=mixing_elbow_geometry_filename)
    geo_import.Execute()
    meshing.workflow.TaskObject["Generate the Volume Mesh"].Execute()
    meshing.tui.mesh.check_mesh()
    gz_path = str(Path(temporary_resource_path) / "default_mesh.msh.gz")
    h5_path = str(Path(temporary_resource_path) / "default_mesh.msh.h5")
    meshing.tui.file.write_mesh(gz_path)
    meshing.tui.file.write_mesh(h5_path)
    assert (Path(temporary_resource_path) / "default_mesh.msh.gz").exists() == True
    assert (Path(temporary_resource_path) / "default_mesh.msh.h5").exists() == True

    # Step 3: use created mesh file - .msh.gz/.msh.h5
    meshing.tui.file.read_mesh(gz_path, "ok")
    meshing.tui.file.read_mesh(h5_path, "ok")

    # Step 4: Switch to solution and Write case file
    solver = meshing.switch_to_solver()
    solver.settings.solution.initialization.hybrid_initialize()
    gz_path = str(Path(temporary_resource_path) / "default_case.cas.gz")
    h5_path = str(Path(temporary_resource_path) / "default_case.cas.h5")
    write_case = solver.settings.file.write_case
    write_case(file_name=gz_path)
    write_case(file_name=h5_path)
    assert (Path(temporary_resource_path) / "default_case.cas.gz").exists() == True
    assert (Path(temporary_resource_path) / "default_case.cas.h5").exists() == True
    solver.exit()
    shutil.rmtree(temporary_resource_path, ignore_errors=True)


@pytest.mark.nightly
@pytest.mark.codegen_required
@pytest.mark.fluent_version("latest")
def test_case_file():
    case_path = examples.download_file("elbow_param.cas.h5", "pyfluent/mixing_elbow")
    reader = CaseFile(case_file_name=case_path)

    assert reader.num_dimensions() == 3
    assert reader.precision() == 2

    plist = []
    olist = []
    for p in reader.input_parameters():
        ipar = OrderedDict()
        ipar["name"] = p.name
        ipar["numeric_value"] = p.numeric_value
        ipar["units"] = p.units
        plist.append(ipar)

    input_params = plist[0]
    assert input_params["name"] == "inlet2_temp"
    assert input_params["numeric_value"] == 500.0
    assert input_params["units"] == "K"

    for o in reader.output_parameters():
        opar = OrderedDict()
        opar["name"] = o.name
        opar["numeric_value"] = 0.0
        opar["units"] = o.units
        olist.append(opar)

    output_params = olist[0]
    assert output_params["name"] == "outlet_temp-op"
    assert output_params["numeric_value"] == 0.0
    assert output_params["units"] == "K"


@pytest.mark.nightly
@pytest.mark.codegen_required
@pytest.mark.fluent_version("latest")
def test_parameters(mixing_elbow_param_case_data_session):
    solver_session = mixing_elbow_param_case_data_session
    input_params = solver_session.settings.parameters.input_parameters.expression[
        "inlet2_temp"
    ]
    assert input_params() == {"name": "inlet2_temp", "value": 500.0}

    output_params = solver_session.settings.parameters.output_parameters.list()
    output_jdict = {}
    for key, entry in output_params.items():
        output_jdict[key] = entry[0]
        output_jdict[key] = entry[1]

    assert output_jdict == {"outlet_temp-op": ["temperature", False]}


@pytest.mark.nightly
@pytest.mark.codegen_required
@pytest.mark.fluent_version("latest")
def test_parametric_project(mixing_elbow_param_case_data_session, new_solver_session):
    session1 = mixing_elbow_param_case_data_session
    Path(pyfluent.EXAMPLES_PATH).mkdir(parents=True, exist_ok=True)
    tmp_save_path = tempfile.mkdtemp(dir=pyfluent.EXAMPLES_PATH)
    init_project = Path(tmp_save_path) / "mixing_elbow_param_init.flprj"
    project_file = Path(tmp_save_path) / "mixing_elbow_param.flprj"
    session1.settings.parametric_studies.initialize(project_filename=str(init_project))
    session1.settings.file.parametric_project.save_as(
        project_filename=str(project_file)
    )
    assert project_file.exists()

    session2 = new_solver_session
    session2.settings.file.parametric_project.open(project_filename=str(project_file))
    current_pstudy_name = session2.settings.current_parametric_study()
    assert current_pstudy_name == "elbow_param-Solve"
    pstudy = session2.settings.parametric_studies[current_pstudy_name]
    base_dp = pstudy.design_points["Base DP"]()
    base_inputs = base_dp["input_parameters"]
    assert base_inputs == {"inlet2_temp": 500.0}
    base_outputs = base_dp["output_parameters"]
    assert base_outputs == {"outlet_temp-op": 322.336008}
    if session2.get_fluent_version() < FluentVersion.v251:
        pstudy.design_points.create_1()
    else:
        pstudy.design_points.create()
    dp = pstudy.design_points["DP1"]
    dp.input_parameters["inlet2_temp"] = 600.0
    pstudy.design_points.update_selected(design_points=["DP1"])
    fluent_output_table = dp.output_parameters()
    assert fluent_output_table["outlet_temp-op"] != 0.0
