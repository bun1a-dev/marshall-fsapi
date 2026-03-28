from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import MediaPlayerEntityFeature

from .const import SOURCE_MAP, SOURCE_MAP_REVERSE, VOLUME_MAX, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MarshallPlayer(coordinator)])


class MarshallPlayer(MediaPlayerEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def name(self):
        return "Marshall Speaker"

    @property
    def volume_level(self):
        return self.coordinator.data["volume"] / VOLUME_MAX

    async def async_set_volume_level(self, volume):
        await self.coordinator.async_set(
            "netRemote.sys.audio.volume", int(volume * VOLUME_MAX)
        )

    @property
    def source(self):
        return SOURCE_MAP.get(self.coordinator.data["source"], "Unknown")

    @property
    def source_list(self):
        return list(SOURCE_MAP.values())

    async def async_select_source(self, source):
        await self.coordinator.async_set(
            "netRemote.sys.mode", SOURCE_MAP_REVERSE[source]
        )

    async def async_media_play(self):
        await self.coordinator.async_set("netRemote.play.control", 1)

    async def async_media_pause(self):
        await self.coordinator.async_set("netRemote.play.control", 2)

    async def async_media_next_track(self):
        await self.coordinator.async_set("netRemote.play.control", 3)

    async def async_media_previous_track(self):
        await self.coordinator.async_set("netRemote.play.control", 4)

    @property
    def supported_features(self):
        return (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.SELECT_SOURCE
            | MediaPlayerEntityFeature.MEDIA_PLAY
            | MediaPlayerEntityFeature.MEDIA_PAUSE
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.PREVIOUS_TRACK
        )

    async def async_update(self):
        await self.coordinator.async_request_refresh()