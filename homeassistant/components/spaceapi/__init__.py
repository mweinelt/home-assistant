"""Support for the SpaceAPI: https://spaceapi.io/docs/"""

from contextlib import suppress

import voluptuous as vol

from homeassistant.components.http import KEY_HASS, HomeAssistantView
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_ICON,
    ATTR_LOCATION,
    ATTR_NAME,
    ATTR_STATE,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_ADDRESS,
    CONF_EMAIL,
    CONF_ENTITY_ID,
    CONF_LOCATION,
    CONF_SENSORS,
    CONF_STATE,
    CONF_URL,
)
import homeassistant.core as ha
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.template import area_name as get_area_name
from homeassistant.helpers.typing import ConfigType
import homeassistant.util.dt as dt_util

ATTR_API_COMPATIBILITY = "api_compatibility"
ATTR_ADDRESS = "address"
ATTR_SPACEFED = "spacefed"
ATTR_CAM = "cam"
ATTR_FEEDS = "feeds"
ATTR_PROJECTS = "projects"
ATTR_LAT = "lat"
ATTR_LON = "lon"
ATTR_TIMEZONE = "timezone"
ATTR_CLOSED = "closed"
ATTR_CONTACT = "contact"
ATTR_LASTCHANGE = "lastchange"
ATTR_LOGO = "logo"
ATTR_OPEN = "open"
ATTR_SENSORS = "sensors"
ATTR_SPACE = "space"
ATTR_UNIT = "unit"
ATTR_URL = "url"
ATTR_VALUE = "value"
ATTR_SENSOR_LOCATION = "location"

CONF_CONTACT = "contact"
CONF_EXTENSIONS = "extensions"
CONF_HUMIDITY = "humidity"
CONF_ICON_CLOSED = "icon_closed"
CONF_ICON_OPEN = "icon_open"
CONF_ICONS = "icons"
CONF_IRC = "irc"
CONF_SPACEFED = "spacefed"
CONF_SPACENET = "spacenet"
CONF_SPACESAML = "spacesaml"
CONF_SPACEPHONE = "spacephone"
CONF_CAM = "cam"
CONF_FEEDS = "feeds"
CONF_FEED_BLOG = "blog"
CONF_FEED_WIKI = "wiki"
CONF_FEED_CALENDAR = "calendar"
CONF_FEED_FLICKER = "flicker"
CONF_FEED_TYPE = "type"
CONF_FEED_URL = "url"
CONF_CACHE = "cache"
CONF_CACHE_SCHEDULE = "schedule"
CONF_PROJECTS = "projects"
CONF_LOGO = "logo"
CONF_PHONE = "phone"
CONF_SIP = "sip"
CONF_KEYMASTERS = "keymasters"
CONF_KEYMASTER_NAME = "name"
CONF_KEYMASTER_IRC_NICK = "irc_nick"
CONF_KEYMASTER_PHONE = "phone"
CONF_KEYMASTER_EMAIL = "email"
CONF_KEYMASTER_TWITTER = "twitter"
CONF_KEYMASTER_XMPP = "xmpp"
CONF_KEYMASTER_MASTODON = "mastodon"
CONF_KEYMASTER_MATRIX = "matrix"
CONF_TWITTER = "twitter"
CONF_FACEBOOK = "facebook"
CONF_IDENTICA = "identica"
CONF_FOURSQUARE = "foursquare"
CONF_ML = "ml"
CONF_MASTODON = "mastodon"
CONF_GOPHER = "gopher"
CONF_MATRIX = "matrix"
CONF_MUMBLE = "mumble"
CONF_XMPP = "xmpp"
CONF_ISSUE_MAIL = "issue_mail"
CONF_SPACE = "space"
CONF_TEMPERATURE = "temperature"
CONF_TIMEZONE = "timezone"

DATA_SPACEAPI = "data_spaceapi"
DOMAIN = "spaceapi"

SENSOR_TYPES = [CONF_HUMIDITY, CONF_TEMPERATURE]
SPACEAPI_VERSION = "14"

URL_API_SPACEAPI = "/api/spaceapi"

LOCATION_SCHEMA = vol.Schema(
    {vol.Optional(CONF_ADDRESS): cv.string, vol.Optional(CONF_TIMEZONE): cv.string}
)

SPACEFED_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SPACENET): cv.boolean,
        vol.Optional(CONF_SPACESAML): cv.boolean,
        vol.Optional(CONF_SPACEPHONE): cv.boolean,
    }
)

FEED_SCHEMA = vol.Schema(
    {vol.Optional(CONF_FEED_TYPE): cv.string, vol.Required(CONF_FEED_URL): cv.url}
)

FEEDS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_FEED_BLOG): FEED_SCHEMA,
        vol.Optional(CONF_FEED_WIKI): FEED_SCHEMA,
        vol.Optional(CONF_FEED_CALENDAR): FEED_SCHEMA,
        vol.Optional(CONF_FEED_FLICKER): FEED_SCHEMA,
    }
)

KEYMASTER_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_KEYMASTER_NAME): cv.string,
        vol.Optional(CONF_KEYMASTER_IRC_NICK): cv.string,
        vol.Optional(CONF_KEYMASTER_PHONE): cv.string,
        vol.Optional(CONF_KEYMASTER_EMAIL): cv.string,
        vol.Optional(CONF_KEYMASTER_TWITTER): cv.string,
        vol.Optional(CONF_KEYMASTER_XMPP): cv.string,
        vol.Optional(CONF_KEYMASTER_MASTODON): cv.string,
        vol.Optional(CONF_KEYMASTER_MATRIX): cv.string,
    }
)

CONTACT_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_EMAIL): cv.string,
        vol.Optional(CONF_FACEBOOK): cv.string,
        vol.Optional(CONF_FOURSQUARE): cv.string,
        vol.Optional(CONF_GOPHER): cv.string,
        vol.Optional(CONF_IDENTICA): cv.string,
        vol.Optional(CONF_IRC): cv.string,
        vol.Optional(CONF_ISSUE_MAIL): cv.string,
        vol.Optional(CONF_MASTODON): cv.string,
        vol.Optional(CONF_MATRIX): cv.string,
        vol.Optional(CONF_ML): cv.string,
        vol.Optional(CONF_MUMBLE): cv.string,
        vol.Optional(CONF_PHONE): cv.string,
        vol.Optional(CONF_SIP): cv.string,
        vol.Optional(CONF_TWITTER): cv.string,
        vol.Optional(CONF_XMPP): cv.string,
        vol.Optional(CONF_KEYMASTERS): vol.All(
            cv.ensure_list, [KEYMASTER_SCHEMA], vol.Length(min=1)
        ),
    },
    required=False,
)

STATE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): cv.entity_id,
        vol.Inclusive(CONF_ICON_CLOSED, CONF_ICONS): cv.url,
        vol.Inclusive(CONF_ICON_OPEN, CONF_ICONS): cv.url,
    },
    required=False,
)

SENSOR_SCHEMA = vol.Schema(
    {vol.In(SENSOR_TYPES): [cv.entity_id], cv.string: [cv.entity_id]}
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_CONTACT): CONTACT_SCHEMA,
                vol.Optional(CONF_LOCATION): LOCATION_SCHEMA,
                vol.Required(CONF_LOGO): cv.url,
                vol.Required(CONF_SPACE): cv.string,
                vol.Required(CONF_STATE): STATE_SCHEMA,
                vol.Required(CONF_URL): cv.string,
                vol.Optional(CONF_SENSORS): SENSOR_SCHEMA,
                vol.Optional(CONF_SPACEFED): SPACEFED_SCHEMA,
                vol.Optional(CONF_CAM): vol.All(
                    cv.ensure_list, [cv.url], vol.Length(min=1)
                ),
                vol.Optional(CONF_FEEDS): FEEDS_SCHEMA,
                vol.Optional(CONF_PROJECTS): vol.All(cv.ensure_list, [cv.url]),
                vol.Optional(CONF_EXTENSIONS): dict,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the SpaceAPI with the HTTP interface."""
    hass.data[DATA_SPACEAPI] = config[DOMAIN]
    hass.http.register_view(APISpaceApiView)

    return True


class APISpaceApiView(HomeAssistantView):
    """View to provide details according to the SpaceAPI."""

    url = URL_API_SPACEAPI
    name = "api:spaceapi"

    @staticmethod
    def get_sensor_data(hass, spaceapi, sensor):
        """Get data from a sensor."""
        if not (sensor_state := hass.states.get(sensor)):
            return None
        try:
            sensor_data = {ATTR_NAME: sensor_state.name, ATTR_VALUE: float(sensor_state.state)}
        except ValueError as ex:
            # casting to float likely didn't pan out
            return None

        if ATTR_SENSOR_LOCATION in sensor_state.attributes:
            sensor_data[ATTR_LOCATION] = sensor_state.attributes[ATTR_SENSOR_LOCATION]
        elif area_name := get_area_name(hass, sensor_state.entity_id):
            sensor_data[ATTR_LOCATION] = area_name
        else:
            sensor_data[ATTR_LOCATION] = spaceapi[CONF_SPACE]

        # Some sensors don't have a unit of measurement
        if ATTR_UNIT_OF_MEASUREMENT in sensor_state.attributes:
            sensor_data[ATTR_UNIT] = sensor_state.attributes[ATTR_UNIT_OF_MEASUREMENT]
        return sensor_data

    @ha.callback
    def get(self, request):
        """Get SpaceAPI data."""
        hass = request.app[KEY_HASS]
        spaceapi = dict(hass.data[DATA_SPACEAPI])
        is_sensors = spaceapi.get("sensors")

        location = {ATTR_LAT: hass.config.latitude, ATTR_LON: hass.config.longitude}

        try:
            location[ATTR_ADDRESS] = spaceapi[ATTR_LOCATION][CONF_ADDRESS]
            location[ATTR_TIMEZONE] = spaceapi[ATTR_LOCATION][CONF_TIMEZONE]
        except KeyError:
            pass
        except TypeError:
            pass

        state_entity = spaceapi["state"][ATTR_ENTITY_ID]

        if (space_state := hass.states.get(state_entity)) is not None:
            state = {
                ATTR_OPEN: space_state.state not in ["off", "False"],
                ATTR_LASTCHANGE: dt_util.as_timestamp(space_state.last_updated),
            }
        else:
            state = {ATTR_OPEN: "null", ATTR_LASTCHANGE: 0}

        with suppress(KeyError):
            state[ATTR_ICON] = {
                ATTR_OPEN: spaceapi["state"][CONF_ICON_OPEN],
                ATTR_CLOSED: spaceapi["state"][CONF_ICON_CLOSED],
            }

        data = {
            ATTR_API_COMPATIBILITY: [SPACEAPI_VERSION],
            ATTR_CONTACT: spaceapi[CONF_CONTACT],
            ATTR_LOCATION: location,
            ATTR_LOGO: spaceapi[CONF_LOGO],
            ATTR_SPACE: spaceapi[CONF_SPACE],
            ATTR_STATE: state,
            ATTR_URL: spaceapi[CONF_URL],
        }

        with suppress(KeyError):
            data[ATTR_CAM] = spaceapi[CONF_CAM]

        with suppress(KeyError):
            data[ATTR_SPACEFED] = spaceapi[CONF_SPACEFED]

        with suppress(KeyError):
            data[ATTR_FEEDS] = spaceapi[CONF_FEEDS]

        with suppress(KeyError):
            data[ATTR_PROJECTS] = spaceapi[CONF_PROJECTS]

        if is_sensors is not None:
            sensors = {}
            for sensor_type in is_sensors:
                sensors[sensor_type] = []
                for sensor in spaceapi["sensors"][sensor_type]:
                    sensor_data = self.get_sensor_data(hass, spaceapi, sensor)
                    sensors[sensor_type].append(sensor_data)
            data[ATTR_SENSORS] = sensors

        with suppress(KeyError):
            data.update(spaceapi[CONF_EXTENSIONS])

        return self.json(data)
