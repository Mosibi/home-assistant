"""
homeassistant.components.switch.transmission
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Enable or disable Transmission BitTorrent client Turtle Mode.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.transmission/
"""
import logging

from homeassistant.const import (CONF_HOST, CONF_USERNAME, CONF_PASSWORD,
                                 STATE_ON, STATE_OFF)
from homeassistant.helpers.entity import ToggleEntity

_LOGGING = logging.getLogger(__name__)
REQUIREMENTS = ['transmissionrpc==0.11']


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """ Sets up the transmission sensor. """
    import transmissionrpc
    from transmissionrpc.error import TransmissionError

    host = config.get(CONF_HOST)
    username = config.get(CONF_USERNAME, None)
    password = config.get(CONF_PASSWORD, None)
    port = config.get('port', 9091)

    name = config.get("name", "Transmission Turtle Mode")
    if not host:
        _LOGGING.error('Missing config variable %s', CONF_HOST)
        return False

    # import logging
    # logging.getLogger('transmissionrpc').setLevel(logging.DEBUG)

    transmission_api = transmissionrpc.Client(
        host, port=port, user=username, password=password)
    try:
        transmission_api.session_stats()
    except TransmissionError:
        _LOGGING.exception("Connection to Transmission API failed.")
        return False

    add_devices_callback([
        TransmissionSwitch(transmission_api, name)
    ])


class TransmissionSwitch(ToggleEntity):
    """ A Transmission sensor. """

    def __init__(self, transmission_client, name):
        self._name = name
        self.transmission_client = transmission_client
        self._state = STATE_OFF

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        """ Returns the state of the device. """
        return self._state

    @property
    def should_poll(self):
        """ Poll for status regularly. """
        return True

    @property
    def is_on(self):
        """ True if device is on. """
        return self._state == STATE_ON

    def turn_on(self, **kwargs):
        """ Turn the device on. """

        _LOGGING.info("Turning on Turtle Mode")
        self.transmission_client.set_session(
            alt_speed_enabled=True)

    def turn_off(self, **kwargs):
        """ Turn the device off. """

        _LOGGING.info("Turning off Turtle Mode ")
        self.transmission_client.set_session(
            alt_speed_enabled=False)

    def update(self):
        """ Gets the latest data from Transmission and updates the state. """

        active = self.transmission_client.get_session(
        ).alt_speed_enabled
        self._state = STATE_ON if active else STATE_OFF
