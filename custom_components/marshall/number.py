from homeassistant.components.number import NumberEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            MarshallBass(coordinator),
            MarshallTreble(coordinator),
        ]
    )


class MarshallBass(NumberEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def name(self):
        return "Marshall Bass"

    @property
    def native_value(self):
        return self.coordinator.data["bass"]

    @property
    def native_min_value(self):
        return 0

    @property
    def native_max_value(self):
        return 10

    async def async_set_native_value(self, value):
        await self.coordinator.async_set(
            "netRemote.sys.audio.eqCustom.param0", int(value)
        )
        await self.coordinator.async_request_refresh()


class MarshallTreble(NumberEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def name(self):
        return "Marshall Treble"

    @property
    def native_value(self):
        return self.coordinator.data["treble"]

    @property
    def native_min_value(self):
        return 0

    @property
    def native_max_value(self):
        return 10

    async def async_set_native_value(self, value):
        await self.coordinator.async_set(
            "netRemote.sys.audio.eqCustom.param1", int(value)
        )
        await self.coordinator.async_request_refresh()