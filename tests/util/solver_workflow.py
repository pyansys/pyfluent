import pytest

import ansys.fluent.core as pyfluent


def create_solver_session(*args, **kwargs):
    return pyfluent.launch_fluent(**kwargs)


@pytest.fixture
def new_solver_session():
    solver = create_solver_session()
    yield solver
    solver.exit(timeout=5, timeout_force=True)


# To use in tests which immediately reads a case after using the fixture
@pytest.fixture(scope="session")
def new_solver_session_read_case_session_scope():
    solver = create_solver_session()
    yield solver
    solver.exit(timeout=5, timeout_force=True)


@pytest.fixture(scope="session")
def new_solver_session_scoped_session():
    solver = create_solver_session()
    yield solver
    solver.exit(timeout=5, timeout_force=True)


@pytest.fixture
def make_new_session():
    sessions = []

    def _make_new_session(**kwargs):
        session = pyfluent.launch_fluent(**kwargs)
        sessions.append(session)
        return session

    yield _make_new_session

    for session in sessions:
        session.exit(timeout=5, timeout_force=True)


@pytest.fixture
def new_solver_session_single_precision():
    solver = create_solver_session(precision="single")
    yield solver
    solver.exit(timeout=5, timeout_force=True)


@pytest.fixture
def new_solver_session_no_transcript():
    solver = create_solver_session(start_transcript=False, mode="solver")
    yield solver
    solver.exit(timeout=5, timeout_force=True)


# To use in tests which immediately reads a case after using the fixture
@pytest.fixture(scope="session")
def new_solver_session_no_transcript_read_case_scoped_session():
    solver = create_solver_session(start_transcript=False, mode="solver")
    yield solver
    solver.exit(timeout=5, timeout_force=True)
