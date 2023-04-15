import discord
from discord.app_commands import CheckFailure

from .BaseMusicCogCheck import BaseMusicCogCheck

__all__ = ["MusicCogCheck"]


class MusicCogCheck(BaseMusicCogCheck):
    @staticmethod
    def must_not_be_a_stream(interaction: discord.Interaction):
        vc: discord.VoiceClient = interaction.guild.voice_client  # pyright: ignore

        if vc and vc.source and vc.source.is_stream:  # type: ignore
            raise CheckFailure("I can't use this command on streams.")

        return True

    @staticmethod
    def queue_has_element(interaction: discord.Interaction):
        vc: discord.VoiceClient = interaction.guild.voice_client  # pyright: ignore

        if vc and vc.is_empty:  # type: ignore
            raise CheckFailure("I need to have something in the queue.")

        return True
