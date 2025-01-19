.. _ref_events_guide:

.. vale Google.Spacing = NO

Observing events
================

Each session object has an ``events`` child of type :obj:`~ansys.fluent.core.streaming_services.events_streaming.EventsManager`. You can call
the ``events.register_callback()`` method in order to receive notifications of various events
occurring in Fluent. (The :obj:`~ansys.fluent.core.streaming_services.events_streaming.EventsManager` object calls each callback whenever a Fluent
event occurs, passing the relevant session object and event information as arguments to the
callback). The :obj:`~ansys.fluent.core.streaming_services.events_streaming.EventsManager` object is useful for solution monitoring and dynamic update
of graphics.

Supported events are enumerated by the PyFluent :obj:`~ansys.fluent.core.streaming_services.events_streaming.SolverEvent` and :obj:`~ansys.fluent.core.streaming_services.events_streaming.MeshingEvent` classes.

The following code triggers a callback at the end of every iteration.

.. code-block:: python

  >>> from ansys.fluent.core import SolverEvent, IterationEndedEventInfo
  >>>
  >>> def on_iteration_ended(session, event_info: IterationEndedEventInfo):
  >>>     print("Iteration ended. Index = ", event_info.index)
  >>>
  >>> callback_id = solver.events.register_callback(SolverEvent.ITERATION_ENDED, on_iteration_ended)

The general signature of the callback function is ``cb(session, event_info, <additional arguments>)``, where ``session`` is the session instance
and ``event_info`` instance holds information about the event. The event information classes for each event are documented in the
API reference of the :obj:`~ansys.fluent.core.streaming_services.events_streaming` module. See the callback function
``on_case_loaded_with_args()`` in the below examples for an example of how to pass additional arguments to the callback
function.


Examples
--------

.. code-block:: python

  >>> from ansys.fluent.core import MeshingEvent, SolverEvent
  >>> from ansys.fluent.core import CaseLoadedEventInfo, DataLoadedEventInfo, SolutionInitializedEventInfo, IterationEndedEventInfo
  >>> from ansys.fluent.core.utils.event_loop import execute_in_event_loop_threadsafe
  >>> from ansys.fluent.visualization.matplotlib import matplot_windows_manager
  >>> from ansys.fluent.visualization.pyvista import pyvista_windows_manager
  >>> from ansys.fluent.visualization import Graphics
  >>>
  >>> graphics = Graphics(session=solver)
  >>>
  >>> contour1 = graphics.Contours["contour-1"]
  >>> contour1.field = "temperature"
  >>> contour1.surfaces_list = ["symmetry"]
  >>>
  >>> contour2 = graphics.Contours["contour-2"]
  >>> contour2.field = "velocity-magnitude"
  >>> contour2.surfaces_list = ["symmetry"]
  >>> 
  >>> @execute_in_event_loop_threadsafe
  >>> def auto_refersh_call_back_iteration(session, event_info: IterationEndedEventInfo):
  >>>   if event_info.index % 5 == 0:
  >>>       pyvista_windows_manager.refresh_windows(session.id, ["contour-1", "contour-2"])
  >>>       matplot_windows_manager.refresh_windows("", ["residual"])
  >>>
  >>> callback_itr_id = solver.events.register_callback(SolverEvent.ITERATION_ENDED, auto_refersh_call_back_iteration)
  >>>
  >>> @execute_in_event_loop_threadsafe
  >>> def initialize_call_back(session, event_info: SolutionInitializedEventInfo | DataLoadedEventInfo):
  >>>     pyvista_windows_manager.refresh_windows(session.id, ["contour-1", "contour-2"])
  >>>     matplot_windows_manager.refresh_windows("", ["residual"])
  >>>
  >>> callback_init_id = solver.events.register_callback(SolverEvent.SOLUTION_INITIALIZED, initialize_call_back)
  >>>
  >>> callback_data_read_id = solver.events.register_callback(SolverEvent.DATA_LOADED, initialize_call_back)
  >>>
  >>> def on_case_loaded(session, event_info: CaseLoadedEventInfo):
  >>>     print("Case loaded. Index = ", event_info.index)
  >>>
  >>> def on_case_loaded_with_args(session, event_info: CaseLoadedEventInfo, x, y):
  >>>     print(f"Case loaded with {x}, {y}. Index = ", event_info.index)
  >>>
  >>> callback = meshing.events.register_callback(MeshingEvent.CASE_LOADED, on_case_loaded)
  >>>
  >>> callback_case = solver.events.register_callback(SolverEvent.CASE_LOADED, on_case_loaded)
  >>>
  >>> callback_case_with_args = solver.events.register_callback(SolverEvent.CASE_LOADED, on_case_loaded_with_args, 12, y=42)
  >>>
