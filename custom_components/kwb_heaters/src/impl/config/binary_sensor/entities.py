from collections.abc import Iterable
import logging

from homeassistant.components.binary_sensor import BinarySensorDeviceClass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ....api.platform.binary_sensor.binary_sensor_coordinated import (
    CoordinatedBinarySensor,
)
from ....api.platform.binary_sensor.binary_sensor_description import (
    BinarySensorDescription,
)

logger = logging.getLogger(__name__)


def setup_entities(
    device_info: DeviceInfo,
    coordinator: DataUpdateCoordinator,
    config_entry: ConfigEntry,
) -> Iterable[Entity]:
    """Transform pykwb signal maps into KWBSensorEntityDescriptions.

    Do not do any IO in this method. It is not async and so will
    block the HomeAssistant event loop.
    """

    # TODO refactor out this chunk. Same in sensors.entities.py
    unique_device_id = list(device_info.get("identifiers"))[0][1]
    model = device_info.get("model")

    entities = []

    # NOTE: Boolean ("b") signals are intentionally NOT registered as binary
    # sensors here. They are created as regular sensors in
    # sensor/entities.py so their raw values (0/1) are shown instead of
    # "In Betrieb"/"Außer Betrieb". Registering them here as well would create
    # duplicate entities for the same signal.

    entities.append(
        CoordinatedBinarySensor(
            coordinator=coordinator,
            device_info=device_info,
            entity_description=BinarySensorDescription(
                key="boiler_on",
                translation_key="boiler_on",
                name=f"{model} {unique_device_id} Boiler On",
                device_class=BinarySensorDeviceClass.RUNNING,
            ),
        )
    )

    return entities
