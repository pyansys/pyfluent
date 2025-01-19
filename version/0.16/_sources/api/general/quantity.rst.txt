.. _ref_quantity:

Quantity
========

.. code-block:: python

    >>> import ansys.fluent.core.quantity.quantity as q
    >>> velocity_1 = q.Quantity(20.2, units="m s^-1")
    >>> velocity_1
    Quantity (20.2, "m s^-1")
    >>> velocity_2 = q.Quantity(30.2, dimensions=[0.0, 1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    >>> velocity_2
    Quantity (30.2, "m s^-1")
    >>> velocity_3 = q.Quantity(40.2, quantity_map={"Velocity": 1.0})
    >>> velocity_3
    Quantity (40.2, "m s^-1")
    >>> velocity_1.value
    20.2
    >>> velocity_1.units
    'm s^-1'
    >>> velocity_1.si_value
    20.2
    >>> velocity_1.si_units
    'm s^-1'
    >>> velocity_1.type
    'Composite'
    >>> velocity_1.is_dimensionless
    False
    >>> velocity_1.dimensions
    [0.0, 1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    >>> velocity_1.to("ft s^-1")
    Quantity (66.2729658792651, "ft s^-1")
    >>> velocity_1 ** 2
    Quantity (408.03999999999996, "m^2 s^-2")
    >>> velocity_2 + velocity_1
    Quantity (50.4, "m s^-1")
    >>> velocity_2 - velocity_1
    Quantity (10.0, "m s^-1")
    >>> velocity_2 * velocity_1
    Quantity (610.04, "m^2 s^-2")
    >>> velocity_2 / velocity_1
    Quantity (1.495049504950495, "")
    >>> velocity_3 > velocity_1
    True
    >>> velocity_3 >= velocity_2
    True
    >>> velocity_1 < velocity_2
    True
    >>> velocity_1 <= velocity_3
    True
    >>> velocity_1 == velocity_2
    False
    >>> velocity_1 != velocity_3
    True

.. automodule:: ansys.fluent.core.quantity.quantity
   :members:
   :show-inheritance:
   :undoc-members:
   :exclude-members: __weakref__, __dict__
   :special-members: __init__
   :autosummary:

.. automodule:: ansys.fluent.core.quantity.dimensions
   :members:
   :show-inheritance:
   :undoc-members:
   :exclude-members: __weakref__, __dict__
   :special-members: __init__
   :autosummary:

.. automodule:: ansys.fluent.core.quantity.quantity_map
   :members:
   :show-inheritance:
   :undoc-members:
   :exclude-members: __weakref__, __dict__
   :special-members: __init__
   :autosummary:

.. automodule:: ansys.fluent.core.quantity.units_table
   :members:
   :show-inheritance:
   :undoc-members:
   :exclude-members: __weakref__, __dict__
   :special-members: __init__
   :autosummary:
