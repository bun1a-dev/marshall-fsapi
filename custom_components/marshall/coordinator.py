import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import SCAN_INTERVAL


class MarshallCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config):
        self.host = config["host"]
        self.pin = config["pin"]

        super().__init__(
            hass,
            logger=None,
            name="Marshall FSAPI",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _fetch(self, session, path):
        url = f"http://{self.host}/fsapi/GET/{path}?pin={self.pin}"
        async with session.get(url, timeout=5) as resp:
            return await resp.json()

    async def _async_update_data(self):
        async with aiohttp.ClientSession() as session:
            volume = await self._fetch(session, "netRemote.sys.audio.volume")
            bass = await self._fetch(session, "netRemote.sys.audio.eqCustom.param0")
            treble = await self._fetch(session, "netRemote.sys.audio.eqCustom.param1")
            source = await self._fetch(session, "netRemote.sys.mode")

        return {
            "volume": volume["fsapiResponse"]["value"]["u8"],
            "bass": bass["fsapiResponse"]["value"]["s16"],
            "treble": treble["fsapiResponse"]["value"]["s16"],
            "source": source["fsapiResponse"]["value"]["u32"],
        }

    async def async_set(self, path, value):
        url = f"http://{self.host}/fsapi/SET/{path}?pin={self.pin}&value={value}"
        async with aiohttp.ClientSession() as session:
            await session.get(url)