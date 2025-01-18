from discord.ext import commands

from nameless import Nameless

__all__ = ["bot_in_voice"]


def bot_in_voice():
    def predicate(ctx: commands.Context[Nameless]):
        if ctx.guild and ctx.guild.voice_client is None:
            raise commands.CheckFailure("I must be in a voice channel.")

        return True

    return commands.check(predicate)
