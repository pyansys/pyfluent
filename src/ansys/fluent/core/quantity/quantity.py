import ansys.fluent.core.quantity as q


class Quantity(float):
    """Quantity instantiates physical quantities using their real values and
    units. All the instances of this class are converted to base SI units system to have
    consistency in arithmetic operations.

    Parameters
    ----------
    value : int | float
        Real value of quantity.
    units : str
        Unit string representation of quantity.
    quantity_map : dict
        Quantity map representation of quantity.
    dimensions : list
        Dimensions representation of quantity.

    Methods
    -------
    to()
        Converts to given unit string.
    convert()
        Converts to given unit system.

    Returns
    -------
    Quantity instance.
    """

    def __new__(cls, value, units=None, quantity_map=None, dimensions=None):
        if (
            (units and quantity_map)
            or (units and dimensions)
            or (quantity_map and dimensions)
        ):
            raise ValueError(
                "Quantity only accepts 1 of the following: units, quantity_map, dimensions"
            )

        _units_table = q.UnitsTable()
        _value = float(value)

        if units or units == "":
            _unit = units

        if quantity_map:
            units = q.QuantityMap(quantity_map).units
            _unit = units

        if dimensions:
            _dimensions = q.Dimensions(dimensions=dimensions)
            _unit = _dimensions.units

        _type = _units_table.get_type(_unit)
        _, si_multiplier, si_offset = _units_table.si_data(units=_unit)
        _si_value = (
            ((_value + si_offset) * si_multiplier)
            if _type == "Temperature"
            else (_value * si_multiplier)
        )

        return float.__new__(cls, _si_value)

    def __init__(self, value, units=None, quantity_map=None, dimensions=None):
        self._units_table = q.UnitsTable()
        self._value = float(value)

        if units or units == "":
            self._unit = units
            self._dimensions = q.Dimensions(units=units)

        if quantity_map:
            units = q.QuantityMap(quantity_map).units
            self._unit = units
            self._dimensions = q.Dimensions(units=units)

        if dimensions:
            self._dimensions = q.Dimensions(dimensions=dimensions)
            self._unit = self._dimensions.units

        self._type = self._units_table.get_type(self._unit)

        si_units, si_multiplier, si_offset = self._units_table.si_data(units=self._unit)

        self._si_units = si_units[:-1]
        self._si_value = (
            ((self.value + si_offset) * si_multiplier)
            if self.type == "Temperature"
            else (self.value * si_multiplier)
        )

    def _arithmetic_precheck(self, __value, caller=None) -> str:
        """Validate dimensions of quantities.

        Parameters
        ----------
        __value : Quantity | int | float
            Value modifying current quantity object.
        caller : str
            Name of caller function.
        Returns
        -------
        : str
            SI unit string of new quantity.
        """
        # Cannot perform operations between quantities with opposing dimensions
        if isinstance(__value, Quantity) and (self.dimensions != __value.dimensions):
            raise QuantityError(from_unit=self.units, to_unit=__value.units)
        # Cannot perform operations on a non-dimensionless quantity
        if (
            caller not in ["__mul__", "__truediv__"]
            and (not self.is_dimensionless)
            and (not isinstance(__value, Quantity))
            and isinstance(__value, (float, int))
        ):
            raise TypeError(
                f"Error: '{__value}' is incompatible with the current quantity object."
            )

        return (
            "delta_K"
            if self.type in ["Temperature", "Temperature Difference"]
            else self.si_units
        )

    @property
    def value(self):
        """Real value"""
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    @property
    def units(self):
        """Unit string"""
        return self._unit

    @property
    def si_value(self):
        """SI conversion value"""
        return self._si_value

    @property
    def si_units(self):
        """SI conversion unit string"""
        return self._si_units

    @property
    def dimensions(self):
        """Dimensions"""
        return self._dimensions.dimensions

    @property
    def is_dimensionless(self) -> bool:
        """Check if quantity is dimensionless."""
        return all([dim == 0.0 for dim in self.dimensions])

    @property
    def type(self):
        """Type"""
        return self._type

    def to(self, to_units: str) -> "Quantity":
        """Perform quantity conversions.

        Parameters
        ----------
        to_units : str
            Desired unit to be converted to.

        Returns
        -------
        : Quantity
            Quantity object containing desired quantity conversion.
        """

        if not isinstance(to_units, str):
            raise TypeError("'to_units' should be of 'str' type.")

        # Retrieve all SI required SI data and perform conversion
        _, si_multiplier, si_offset = self._units_table.si_data(to_units)
        new_value = (
            ((self.si_value / si_multiplier) - si_offset)
            if self.type == "Temperature"
            else (self.si_value / si_multiplier)
        )

        new_obj = Quantity(value=new_value, units=to_units)

        # Confirm conversion compatibility
        self._arithmetic_precheck(new_obj)

        return new_obj

    def convert(self, to_sys: str) -> "Quantity":
        """Perform unit system conversions.

        Parameters
        ----------
        to_sys : str
            Desired unit system to convert to.

        Returns
        -------
        : Quantity
            Quantity object containing desired unit system conversion.
        """

        # Verify specified system is supported
        if to_sys not in ["SI", "CGS", "BT"]:
            raise ValueError(
                f"'{to_sys}' is not a supported unit system. Only 'SI', 'CGS', 'BT' are supported."
            )

        # Create new dimensions with desired unit system
        new_dim = q.Dimensions(dimensions=self.dimensions, unit_sys=to_sys)

        return Quantity(value=self.value, units=new_dim.units)

    def __str__(self):
        return f'({self.value}, "{self.units}")'

    def __repr__(self):
        return f'Quantity ({self.value}, "{self.units}")'

    def __pow__(self, __value):
        temp_dimensions = [dim * __value for dim in self.dimensions]
        new_si_value = self.si_value**__value
        new_dimensions = q.Dimensions(dimensions=temp_dimensions)
        return Quantity(value=new_si_value, units=new_dimensions.units)

    def __mul__(self, __value):
        new_units = self._arithmetic_precheck(__value, "__mul__")
        if isinstance(__value, Quantity):
            temp_dimensions = [
                dim + __value.dimensions[idx] for idx, dim in enumerate(self.dimensions)
            ]
            new_si_value = self.si_value * __value.si_value
            new_dimensions = q.Dimensions(dimensions=temp_dimensions)
            new_units = new_units if new_units == "delta_K" else new_dimensions.units
            return Quantity(value=new_si_value, units=new_units)

        if isinstance(__value, (float, int)):
            return Quantity(value=self.si_value * __value, units=new_units)

    def __rmul__(self, __value):
        return self.__mul__(__value)

    def __truediv__(self, __value):
        new_units = self._arithmetic_precheck(__value, "__truediv__")
        if isinstance(__value, Quantity):
            temp_dimensions = [
                dim - __value.dimensions[idx] for idx, dim in enumerate(self.dimensions)
            ]
            new_si_value = self.si_value / __value.si_value
            new_dimensions = q.Dimensions(dimensions=temp_dimensions)
            new_units = new_units if new_units == "delta_K" else new_dimensions.units
            return Quantity(value=new_si_value, units=new_units)

        if isinstance(__value, (float, int)):
            return Quantity(value=self.si_value / __value, units=new_units)

    def __rtruediv__(self, __value):
        return self.__truediv__(__value)

    def __add__(self, __value):
        new_units = self._arithmetic_precheck(__value)
        new_value = float(self) + float(__value)
        return Quantity(value=new_value, units=new_units)

    def __radd__(self, __value):
        return self.__add__(__value)

    def __sub__(self, __value):
        new_units = self._arithmetic_precheck(__value)
        new_value = float(self) - float(__value)
        return Quantity(value=new_value, units=new_units)

    def __rsub__(self, __value):
        return self.__sub__(__value)

    def __neg__(self):
        return Quantity(-self.value, self.units)

    def __gt__(self, __value):
        self._arithmetic_precheck(__value)
        return float(self) > float(__value)

    def __ge__(self, __value):
        self._arithmetic_precheck(__value)
        return float(self) >= float(__value)

    def __lt__(self, __value):
        self._arithmetic_precheck(__value)
        return float(self) < float(__value)

    def __le__(self, __value):
        self._arithmetic_precheck(__value)
        return float(self) <= float(__value)

    def __eq__(self, __value):
        self._arithmetic_precheck(__value)
        return float(self) == float(__value)

    def __neq__(self, __value):
        self._arithmetic_precheck(__value)
        return float(self) != float(__value)


class QuantityError(ValueError):
    """Custom quantity errors."""

    def __init__(self, from_unit, to_unit):
        """
        Quantity errors with custom messages.

        Parameters
        ----------
        from_unit: str
            Unit of quantity
        to_unit: str
            Desired conversion unit
        """
        self.from_unit = from_unit
        self.to_unit = to_unit

    def __str__(self):
        return f"'{self.from_unit}' and '{self.to_unit}' have incompatible dimensions."
