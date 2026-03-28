import aiohttp
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class MarshallCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config):
        self.host = config["host"]
        self.pin = config["pin"]

        # używamy HA session zamiast tworzyć własną
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            logger=_LOGGER,  # ✅ FIX
            name="Marshall FSAPI",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _fetch(self, path):
        url = f"http://{self.host}/fsapi/GET/{path}?pin={self.pin}"

        try:
            async with self.session.get(url, timeout=5) as resp:
                if resp.status != 200:
                    _LOGGER.warning("Bad response from Marshall: %s", resp.status)
                    return None
                return await resp.json()

        except Exception as e:
            _LOGGER.error("Marshall fetch error (%s): %s", path, e)
            return None

    async def _async_update_data(self):
        try:
            volume = await self._fetch("netRemote.sys.audio.volume")
            bass = await self._fetch("netRemote.sys.audio.eqCustom.param0")
            treble = await self._fetch("netRemote.sys.audio.eqCustom.param1")
            source = await self._fetch("netRemote.sys.mode")

            if not all([volume, bass, treble, source]):
                _LOGGER.warning("Incomplete data from Marshall, using last state")
                return self.data if self.data else {}

            return {
                "volume": volume["fsapiResponse"]["value"].get("u8", 0),
                "bass": bass["fsapiResponse"]["value"].get("s16", 0),
                "treble": treble["fsapiResponse"]["value"].get("s16", 0),
                "source": source["fsapiResponse"]["value"].get("u32", 0),
            }

        except Exception as e:
            _LOGGER.error("Marshall update failed: %s", e)
            return self.data if self.data else {}

    async def async_set(self, path, value):
        url = f"http://{self.host}/fsapi/SET/{path}?pin={self.pin}&value={value}"

        try:
            async with self.session.get(url, timeout=5) as resp:
                if resp.status != 200:
                    _LOGGER.warning("SET failed (%s): %s", path, resp.status)
        except Exception as e:
            _LOGGER.error("Marshall SET error (%s): %s", path, e)
