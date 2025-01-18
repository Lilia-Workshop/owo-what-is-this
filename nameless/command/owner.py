import logging
import os
import sys

import discord
import discord.ui
from discord import app_commands
from discord.ext import commands

from nameless import Nameless
from nameless.command.check import nameless_check

__all__ = ["OwnerCommand"]


class OwnerCommand(commands.Cog):
    """Commands for owners, always loaded by default."""

    def __init__(self, bot: Nameless):
        self.bot: Nameless = bot

    @app_commands.command()
    @app_commands.guild_only()
    @nameless_check.owns_the_bot()
    async def shutdown(self, interaction: discord.Interaction[Nameless]):
        """Shutdown the bot."""
        await interaction.response.defer()
        await interaction.followup.send("Bye owo!")

        await self.bot.close()

    @app_commands.command()
    @app_commands.guild_only()
    @nameless_check.owns_the_bot()
    async def restart(self, interaction: discord.Interaction[Nameless]):
        """Restart the bot."""
        await interaction.response.defer()
        await interaction.followup.send("See you soon!")

        os.execl(sys.executable, sys.executable, *sys.argv)

    @app_commands.command()
    @app_commands.guild_only()
    @nameless_check.owns_the_bot()
    async def refresh_command_list(self, interaction: discord.Interaction[Nameless]):
        """Refresh command list."""
        await interaction.response.defer()

        for guild in interaction.client.guilds:
            self.bot.tree.clear_commands(guild=guild)
            await self.bot.tree.sync(guild=guild)

        self.bot.tree.clear_commands(guild=None)
        await self.bot.tree.sync(guild=None)

        await interaction.followup.send("Command cleaning done, you should restart me to update the new commands.")


async def setup(bot: Nameless):
    await bot.add_cog(OwnerCommand(bot))
    logging.info("%s added!", __name__)


async def teardown(bot: Nameless):
    await bot.remove_cog(OwnerCommand.__cog_name__)
    logging.warning("%s removed!", __name__)
