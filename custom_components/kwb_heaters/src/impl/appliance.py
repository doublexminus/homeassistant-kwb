"""Glue code that allows HomeAssistant to get data from pykwb."""

import logging
import socket

from pykwb.kwb import KWBMessageStream, TCPByteReader, load_signal_maps

from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TIMEOUT, CONF_UNIQUE_ID

from ...const import (
    CONF_BOILER_EFFICIENCY,
    CONF_BOILER_NOMINAL_POWER,
    CONF_PELLET_NOMINAL_ENERGY,
    OPT_LAST_BOILER_RUN_TIME,
    OPT_LAST_ENERGY_OUTPUT,
    OPT_LAST_PELLET_CONSUMPTION,
    OPT_LAST_TIMESTAMP,
)

logger = logging.getLogger(__name__)


class Appliance:
    """A physical appliance or service."""

    def __init__(self, config, signal_maps):
        reader = TCPByteReader(ip=config.get(CONF_HOST), port=config.get(CONF_PORT))
        self.unique_id = config.get(CONF_UNIQUE_ID)
        self.unique_key = config.get(CONF_UNIQUE_ID).lower().replace(" ", "_")
        heater_config = {
            "pellet_nominal_energy_kWh_kg": config.get(CONF_PELLET_NOMINAL_ENERGY),
            "boiler_efficiency": config.get(CONF_BOILER_EFFICIENCY),
            "boiler_nominal_power_kW": config.get(CONF_BOILER_NOMINAL_POWER),
        }
        last_values = {
            "last_timestamp": config.get(OPT_LAST_TIMESTAMP),
            "boiler_run_time": config.get(OPT_LAST_BOILER_RUN_TIME),
            "boiler_energy": config.get(OPT_LAST_ENERGY_OUTPUT),
            "pellet_consumption": config.get(OPT_LAST_PELLET_CONSUMPTION),
        }
        self.message_stream = KWBMessageStream(
            reader=reader,
            signal_maps=signal_maps,
            heater_config=heater_config,
            last_values=last_values,
        )
        # FIXME remove hard coded ids
        self.message_ids = [32, 33, 64, 65]
        self.read_timeout = config.get(CONF_TIMEOUT, 2)
        # TODO support serial too
        # if args.mode == PROP_MODE_TCP:
        #     reader = TCPByteReader(ip=args.hostname, port=args.port)
        # elif args.mode == PROP_MODE_SERIAL:
        #   reader = SerialByteReader(dev=args.interface, baud=args.baud)

        # State variables
        self.latest_scrape = {}

    def scrape(self):
        try:
            self.message_stream.open()
        except (OSError, socket.error) as e:
            host = getattr(self.message_stream.reader, "ip", "?")
            logger.warning("KWB heater TCP connection failed (host=%s): %s", host, e)
            raise

        try:
            datas = list(self.message_stream.read_data(self.message_ids, self.read_timeout))
        finally:
            self.message_stream.close()

        if not datas:
            logger.warning(
                "KWB heater returned no data within timeout=%ss for message_ids=%s. "
                "The heater may be offline or the timeout too short.",
                self.read_timeout,
                self.message_ids,
            )
            return False

        self.latest_scrape.update(datas[-1])
        logger.debug("Scraped %d data keys from KWB heater", len(datas[-1]))
        return True


def create_appliance(config_heater: dict) -> tuple[bool, Appliance | Exception]:
    def f():
        try:
            signal_maps = load_signal_maps()
            heater = Appliance(config_heater, signal_maps)
            is_success = heater.scrape()
        except Exception as e:
            logger.error("Error connecting to heater", exc_info=e)
            return False, e
        return is_success, heater

    return f


def connect_appliance(config_heater: dict) -> tuple[bool, Appliance | Exception]:
    """Called by config_flow.py"""

    def f():
        try:
            is_success, heater = create_appliance(config_heater)()
        except Exception as e:
            return False, e

        return is_success, heater

    return f
