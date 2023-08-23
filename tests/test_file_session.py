from ansys.fluent.core.file_session import FileSession
from ansys.fluent.core.services.field_data import SurfaceDataType


def round_off_list_elements(input_list):
    for index, value in enumerate(input_list):
        input_list[index] = round(value, 6)

    return input_list


def test_field_info_data_multi_phase():
    file_session = FileSession()
    file_session.read_case(
        r"C:\ANSYSDev\PyFluent_Dev_01\filesession\mixing_elbow_mul_ph.cas.h5"
    )
    file_session.read_data(
        r"C:\ANSYSDev\PyFluent_Dev_01\filesession\mixing_elbow_mul_ph.dat.h5"
    )

    assert (
        file_session.field_data.get_scalar_field_data("phase-2:SV_DENSITY", [33])[
            33
        ].size
        == 268
    )
    assert (
        file_session.field_data.get_scalar_field_data("phase-2:SV_DENSITY", [33])[33][
            130
        ].scalar_data
        == 1.225
    )
    assert (
        round(
            file_session.field_data.get_scalar_field_data(
                "phase-2:SV_WALL_YPLUS", [33]
            )[33][130].scalar_data,
            5,
        )
        == 0.00103
    )


def test_field_info_data_single_phase():
    file_session = FileSession()
    file_session.read_case(r"C:\ANSYSDev\PyFluent_Dev_01\filesession\elbow1.cas.h5")
    file_session.read_data(r"C:\ANSYSDev\PyFluent_Dev_01\filesession\elbow1.dat.h5")

    assert round_off_list_elements(
        file_session.field_info.get_scalar_field_range("SV_D")
    ) == [0.000236, 1.64046]
    assert len(file_session.field_info.get_scalar_fields_info()) == 30
    assert list(file_session.field_info.get_surfaces_info().keys()) == [
        "wall",
        "symmetry",
        "pressure-outlet-7",
        "velocity-inlet-6",
        "velocity-inlet-5",
        "default-interior",
    ]

    assert (
        file_session.field_data.get_scalar_field_data("SV_T", surface_name="wall").size
        == 3630
    )
    assert (
        round(
            file_session.field_data.get_scalar_field_data("SV_T", surface_name="wall")[
                1800
            ].scalar_data,
            4,
        )
        == 313.15
    )

    assert (
        file_session.field_data.get_surface_data(
            data_type=SurfaceDataType.Vertices, surface_name="wall"
        ).size
        == 3810
    )
    assert (
        round(
            file_session.field_data.get_surface_data(
                data_type=SurfaceDataType.Vertices, surface_name="wall"
            )[1500].x,
            5,
        )
        == 0.12406
    )
    assert (
        round(
            file_session.field_data.get_surface_data(
                data_type=SurfaceDataType.Vertices, surface_name="wall"
            )[1500].y,
            5,
        )
        == 0.09525
    )
    assert (
        round(
            file_session.field_data.get_surface_data(
                data_type=SurfaceDataType.Vertices, surface_name="wall"
            )[1500].z,
            5,
        )
        == 0.04216
    )

    assert (
        file_session.field_data.get_surface_data(
            data_type=SurfaceDataType.FacesConnectivity, surface_name="symmetry"
        ).size
        == 2018
    )
    assert (
        file_session.field_data.get_surface_data(
            data_type=SurfaceDataType.FacesConnectivity, surface_name="symmetry"
        )[1000].node_count
        == 4
    )
    assert list(
        file_session.field_data.get_surface_data(
            data_type=SurfaceDataType.FacesConnectivity, surface_name="symmetry"
        )[1000].node_indices
    ) == [1259, 1260, 1227, 1226]


def test_data_reader_single_phase():
    file_session = FileSession()
    file_session.read_case(r"C:\ANSYSDev\PyFluent_Dev_01\filesession\elbow1.cas.h5")
    file_session.read_data(r"C:\ANSYSDev\PyFluent_Dev_01\filesession\elbow1.dat.h5")

    assert file_session._data_file.case_file == "elbow1.cas.h5"
    assert file_session._data_file.get_phases() == ["phase-1"]
    assert len(file_session._data_file.get_face_variables("phase-1")) == 30
    assert len(file_session._data_file.get_cell_variables("phase-1")) == 14

    assert file_session._data_file.get_cell_variables("phase-1") == [
        "SV_BF_V",
        "SV_D",
        "SV_DENSITY",
        "SV_H",
        "SV_K",
        "SV_LORENTZ_FORCE",
        "SV_MU_LAM",
        "SV_MU_T",
        "SV_P",
        "SV_T",
        "SV_U",
        "SV_V",
        "SV_W",
        "",
    ]

    assert (
        len(file_session._data_file.get_face_data("phase-1", "SV_DENSITY", 3)) == 3630
    )


def test_data_reader_multi_phase():
    file_session = FileSession()
    file_session.read_case(
        r"C:\ANSYSDev\PyFluent_Dev_01\filesession\mixing_elbow_mul_ph.cas.h5"
    )
    file_session.read_data(
        r"C:\ANSYSDev\PyFluent_Dev_01\filesession\mixing_elbow_mul_ph.dat.h5"
    )

    assert file_session._data_file.case_file == "mixing_elbow_mul_ph.cas.h5"
    assert file_session._data_file.get_phases() == [
        "phase-1",
        "phase-2",
        "phase-3",
        "phase-4",
    ]
    assert len(file_session._data_file.get_face_variables("phase-1")) == 23
    assert len(file_session._data_file.get_face_variables("phase-3")) == 13
    assert len(file_session._data_file.get_cell_variables("phase-2")) == 14

    assert file_session._data_file.get_cell_variables("phase-2") == [
        "SV_BF_V",
        "SV_DENSITY",
        "SV_DENSITY_M1",
        "SV_MU_LAM",
        "SV_MU_T",
        "SV_U",
        "SV_U_M1",
        "SV_V",
        "SV_VOF",
        "SV_VOF_M1",
        "SV_V_M1",
        "SV_W",
        "SV_W_M1",
        "",
    ]

    assert (
        len(file_session._data_file.get_face_data("phase-1", "SV_DENSITY", 33)) == 268
    )
