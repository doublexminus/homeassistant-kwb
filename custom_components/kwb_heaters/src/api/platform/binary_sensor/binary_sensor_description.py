from dataclasses import dataclass, field

from homeassistant.components.binary_sensor import (
    BinarySensorEntityDescription,
)


@dataclass
class BinarySensorDescription(BinarySensorEntityDescription):
    """Extended binary sensor description.

    inverted: if True, the raw value is negated before reporting is_on.
    Use for sensors where True means 'no problem' (e.g. no_interference_state).
    """

    inverted: bool = False
