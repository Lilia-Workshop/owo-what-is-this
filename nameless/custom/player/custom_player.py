# pyright: reportMissingParameterType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false

from wavelink import Player

from .settings import SponsorBlockSettings

__all__ = ["CustomPlayer"]


class CustomPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_channel_id: int = self.channel.id
        self.play_now_allowed: bool = True
        self.sponsorblock_settings: SponsorBlockSettings = SponsorBlockSettings(0)
