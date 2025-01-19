.. _ref_units_guide:

Physical units
==============
By default, you can access and modify PyFluent solver settings according to its S.I. unit.
However, PyFluent also allows you to work in arbitrary physical examples. Here's an example:

.. code-block:: python

  >>> from ansys.units import Quantity
  >>> hydraulic_diameter = solver.settings.setup.boundary_conditions.velocity_inlet["hot-inlet"].turbulence.hydraulic_diameter
  >>> hydraulic_diameter.set_state(.02)
  >>> hydraulic_diameter.get_state()
  0.02
  >>> hydraulic_diameter.state_with_units()
  (0.02, 'm')
  >>> hydraulic_diameter.set_state(Quantity(15, "mm"))
  >>> hydraulic_diameter.state_with_units()
  (0.015, 'm')
  >>> diam = hydraulic_diameter.as_quantity()
  >>> diam
  Quantity (0.015, "m")
  >>> diam = diam * 2
  >>> diam
  Quantity (0.03, "m")
  >>> hydraulic_diameter.set_state(diam)
  >>> hydraulic_diameter.as_quantity()
  Quantity (0.03, "m")


You can find out more about using ``Quantity`` objects and other library features in the 
`PyAnsys Units documentation <https://units.docs.pyansys.com/version/stable/>`_.