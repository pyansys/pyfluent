"""Provides a module for generating Fluent datamodel result files."""

import importlib

from rstgen import _get_file_or_folder, generate


def generate_meshing_datamodels():
    """Generate meshing datamodel result files."""
    meshing_datamodel_roots = []
    meshing_datamodels = [
        "meshing",
        "PartManagement",
        "PMFileManagement",
        "preferences",
        "workflow",
    ]
    for meshing_datamodel in meshing_datamodels:
        datamodel = importlib.import_module(
            f"ansys.fluent.core.{_get_file_or_folder(mode='meshing', is_datamodel=True)}.{meshing_datamodel}"
        )
        meshing_datamodel_roots.append(datamodel.Root)
    for root in meshing_datamodel_roots:
        generate(main_menu=root, mode="meshing", is_datamodel=True)


def generate_solver_datamodels():
    """Generate solver datamodel result files."""
    solver_datamodel_roots = []
    solver_datamodels = ["flicing", "preferences", "solverworkflow", "workflow"]
    for solver_datamodel in solver_datamodels:
        datamodel = importlib.import_module(
            f"ansys.fluent.core.{_get_file_or_folder(mode='solver', is_datamodel=True)}.{solver_datamodel}"
        )
        solver_datamodel_roots.append(datamodel.Root)
    for root in solver_datamodel_roots:
        generate(main_menu=root, mode="solver", is_datamodel=True)


if __name__ == "__main__":
    generate_meshing_datamodels()
    generate_solver_datamodels()
