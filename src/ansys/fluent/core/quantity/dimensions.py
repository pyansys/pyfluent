import ansys.fluent.core.quantity as q


class Dimensions(object):
    """Initialize a Dimensions object using a dimensions list or a unit string.

    Parameters
    ----------
    units: str
        Unit string of quantity.
    dimensions: list
        List of dimensions.

    Returns
    -------
    Dimensions instance.
    """

    def __init__(
        self, units: str = None, dimensions: list = None, unit_sys: str = None
    ):
        self._units_table = q.UnitsTable()
        unit_sys = unit_sys or "SI"
        units = units or " "

        if units:
            self._unit = units
            self._dimensions = self._units_to_dim(units=units)

        if dimensions:
            self._dimensions, self._unit = self._dim_to_units(
                dimensions=dimensions, unit_sys=unit_sys
            )

    def _dim_to_units(self, dimensions: list, unit_sys: str) -> str:
        """Convert a dimensions list into a unit string.

        Parameters
        ----------
        dimensions : list
            List of unit dimensions.

        unit_sys : str
            Unit system of dimensions.

        Returns
        -------
        units : str
            Unit string representation of dimensions.
        """
        # Ensure dimensions list contains 9 terms
        dimensions = [float(dim) for dim in dimensions + ((9 - len(dimensions)) * [0])]
        sys_order = {
            "SI": ["kg", "m", "s", "K", "radian", "mol", "cd", "A", "sr"],
            "CGS": ["g", "cm", "s", "K", "radian", "mol", "cd", "A", "sr"],
            "BT": ["slug", "ft", "s", "R", "radian", "slugmol", "cd", "A", "sr"],
        }
        units = ""

        # Define unit term and associated value from dimension with dimensions list
        for idx, dim in enumerate(dimensions):
            if dim == 1.0:
                units += f"{sys_order[unit_sys][idx]} "
            elif dim != 0.0:
                units += f"{sys_order[unit_sys][idx]}^{dim} "

        return dimensions, units[:-1]

    def _units_to_dim(
        self, units: str, power: float = None, dimensions: list = None
    ) -> list:
        """Convert a unit string into a dimensions list.

        Parameters
        ----------
        units : str
            Unit string of quantity.
        power : float
            Power of unit string.

        Returns
        -------
        dimensions : list
            Dimensions representation of unit string.
        """

        power = power or 1.0
        dimensions = dimensions or [0.0] * 9

        # Split unit string into terms and parse data associated with individual terms
        for term in units.split(" "):
            _, unit_term, unit_term_power = self._units_table.filter_unit_term(term)

            unit_term_power *= power

            # retrieve data associated with fundamental unit
            if unit_term in self._units_table.fundamental_units:
                idx = (
                    self._units_table.fundamental_units[unit_term]["dimension_order"]
                    - 1
                )
                dimensions[idx] += unit_term_power

            # Retrieve derived unit composition unit string and factor.
            if unit_term in self._units_table.derived_units:
                # Recursively parse composition unit string
                dimensions = self._units_to_dim(
                    units=self._units_table.derived_units[unit_term]["composition"],
                    power=unit_term_power,
                    dimensions=dimensions,
                )

        return dimensions

    @property
    def units(self):
        """Unit string representation of dimensions"""
        return self._unit

    @property
    def dimensions(self):
        """Dimensions representation of unit string"""
        return self._dimensions
