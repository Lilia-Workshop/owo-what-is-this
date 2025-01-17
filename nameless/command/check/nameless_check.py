import discord
from discord import app_commands

from nameless import Nameless

__all__ = ["owns_the_bot"]


def owns_the_bot():
    """
    Require the command author to be in the owner(s) list of the bot.
    Note: this is a decorator for an application command.
    """

    async def pred(interaction: discord.Interaction[Nameless], /, **_: object) -> bool:
        nameless: Nameless = interaction.client
        return await nameless.is_owner(interaction.user)

    return app_commands.check(pred)
