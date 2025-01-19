.. _ref_user_guide_tui_commands:

Using TUI commands
==================

TUI commands refer to a programming interface that mirrors the Fluent TUI (text user
interface). There is a TUI command hierarchy defined for each of the two modes: meshing
and solution. The hierarchy that is active depends on the current Fluent mode. The guidance
in this topic applies to both modes.

The PyFluent TUI commands allow you to automate workflows. Everything
that's in the Fluent TUI (which itself is a comprehensive automation interface)
is exposed in PyFluent. The PyFluent TUI commands are Pythonic versions of the
commands that are used in the Fluent console.

The PyFluent TUI commands do not support TUI features such as aliases or
command abbreviation. To make using PyFluent commands in an interactive
session easier, you can install a tool such as
`pyreadline3 <https://github.com/pyreadline3/pyreadline3>`_, which provides
both command line completion and history. To inspect any PyFluent TUI object further,
you can use the Python built-in`help <https://docs.python.org/3/library/functions.html#help>`_
and `dir <https://docs.python.org/3/library/functions.html#dir>`_ functions.

The arguments to a TUI command are those that would be passed in direct interaction in the
Fluent console, but they are in a Pythonic style. The most productive way to write Python commands
is with reference to existing TUI commands. The following examples show how the Python usage
mirrors the existing TUI usage.

TUI command construction
-------------------------
Assume that you are in the solution mode and type the following in the Fluent console to set
velocity inlet properties:

.. code:: lisp

    /define/boundary_conditions/set/velocity-inlet

This command instigates a sequence of prompts in the console. Assume that you respond
to each prompt in turn as follows:

.. code:: lisp

    velocity-inlet-5 
    
    () 
    
    temperature 
    
    no 
    
    293.15 
    
    quit

The following code yields the same result but specifies all arguments in one call:

.. code:: lisp

    /define/boundary-conditions/set/velocity-inlet velocity-inlet-5 () temperature no 293.15 quit

You can see how using the interactive TUI provides a reliable approach for
constructing TUI calls that include full sequences of arguments.

With the full TUI call in hand, you can transform it to a Python call. This
code launches Fluent and makes the call to set velocity inlet properties:

.. code:: python

    from ansys.fluent.core import launch_fluent

    solver_session = launch_fluent(mode="solver")

    tui = solver_session.solver.tui

    tui.define.boundary_conditions.set.velocity_inlet(
      "velocity-inlet-5", [], "temperature", "no", 293.15, "quit"
      )

Here is another Fluent console interaction:

.. code:: scheme

    /define/units

    pressure

    "Pa"

The corresponding Python call is:

.. code:: python

    tui.define.units("pressure", '"Pa"')

To preserve the double quotation marks around the TUI argument,
you must wrap the string ``"Pa"`` in single quotation marks .

TUI command transformation rules
--------------------------------
The following rules are implied in the preceding examples:

- Each forward slash separator between elements in TUI paths is transformed to Python dot notation.
- Some characters in path elements are either removed or replaced because they are illegal inside Python names.
  For example:
  
  - Each hyphen in a path element is transformed to an underscore.
  - Each question mark in a path element is removed.

- Some are some rules about strings:
  
  - String-type arguments must be surrounded by quotation marks in Python.
  - A target Fluent TUI argument that is surrounded by quotation marks (like ``"Pa"`` in the preceding
    example) must be wrapped in single quotation marks so that the original quotation marks are preserved.
  - The contents of string arguments are preserved.

For more examples of TUI command usage, see :ref:`ref_mixing_elbow_tui_api`.
