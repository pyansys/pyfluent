.. _ref_events:

EventsManager
=============

An instance of ``EventsManager`` exists as an active ``events_streaming`` property in each
solution mode session object. You can register client callbacks with the EventsManager.
The EventsManager calls each callback whenever a server-side event occurs, passing the session
ID and event information arguments to the callback. The EventsManager is useful for solution
monitoring and updating graphics during runtime.

Supported events are:

- ``CalculationsEndedEvent``
- ``CalculationsStartedEvent``
- ``CaseReadEvent, DataReadEvent``
- ``InitializedEvent``
- ``IterationEndedEvent``
- ``ProgressEvent``
- ``TimestepEndedEvent``

The following code triggers a callback at the end of every iteration.

.. code-block:: python

    def callback_executed_at_end_of_iteration(session_id, event_info):
        print("Iteration ended index", event_info.index)

    cb_itr_id = session.events.register_callback('IterationEndedEvent', callback_executed_at_end_of_iteration)

.. currentmodule:: ansys.fluent.core.streaming_services.events_streaming

.. autosummary::
    :toctree: _autosummary
    :template: noindex-class.rst
    :recursive:

    EventsManager
