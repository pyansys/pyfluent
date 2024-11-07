import pytest

def _test_systemcoupling_mixing_elbow_settings_common(mixing_elbow_case_data_session):
    solver = mixing_elbow_case_data_session
    # check participant type, analysis type, regions, and variables
    assert solver.system_coupling.participant_type == "FLUENT"
    assert solver.system_coupling.get_analysis_type() == "Steady"
    regions = solver.system_coupling.get_regions()
    variables = solver.system_coupling.get_variables()
    # [wall-inlet, wall-elbow, elbow-fluid, hot-inlet, cold-inlet, outlet]
    assert len(regions) >= 6
    # [force, dsip, temp, htc, hflow, nwt, hrate, cond, lorentz-force]
    assert len(variables) >= 9


@pytest.mark.fluent_version(">=25.1")
def test_systemcoupling_mixing_elbow_settings(mixing_elbow_case_data_session):
    """Very superficial test of System Coupling related settings."""
    _test_systemcoupling_mixing_elbow_settings_common(mixing_elbow_case_data_session)


@pytest.mark.fluent_version("<25.1")
def test_systemcoupling_mixing_elbow_settings_legacy(mixing_elbow_case_data_session):
    """Test legacy implementation of getting System Coupling related settings."""
    _test_systemcoupling_mixing_elbow_settings_common(mixing_elbow_case_data_session)
