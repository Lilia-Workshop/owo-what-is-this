import contextlib
import logging
from typing import override

import discord
from discord import Interaction, InteractionResponded
from discord.app_commands import AppCommandError, CommandTree, errors

from nameless import Nameless
from nameless.config import nameless_config

__all__ = ["NamelessCommandTree"]


class NamelessCommandTree(CommandTree[Nameless]):
    """Custom CommandTree for nameless*, for handling blacklists and custom error handling."""

    def __init__(self, client: Nameless, *, fallback_to_global: bool = True):
        super().__init__(client, fallback_to_global=fallback_to_global)

    async def _is_blacklisted(
        self,
        *,
        user: discord.User | discord.Member | None = None,
        guild: discord.Guild | None = None,
    ) -> bool:
        """Check if an entity is blacklisted from using the bot."""
        # The owners, even if they are in the blacklist, can still use the bot.
        if user and await self.client.is_owner(user):
            return False

        if guild:
            blacklist_guilds: list[int] = nameless_config["blacklist"]["guilds"]
            return guild.id in blacklist_guilds

        if user:
            blacklist_users: list[int] = nameless_config["blacklist"]["users"]
            return user.id in blacklist_users

        return False

    @override
    async def interaction_check(self, interaction: Interaction[Nameless]) -> bool:
        user = interaction.user
        guild = interaction.guild

        is_user_blacklisted = await self._is_blacklisted(user=user)
        is_guild_blacklisted = await self._is_blacklisted(guild=guild)

        if is_user_blacklisted:
            await interaction.response.send_message(
                "You have been blacklisted, please contact the bot owner if needed.",
                ephemeral=True,
            )
            return False

        if is_guild_blacklisted:
            await interaction.response.send_message(
                "This guild has been blacklisted, please contact the guild owner.",
                ephemeral=True,
            )
            return False

        return True

    @override
    async def on_error(self, interaction: Interaction[Nameless], error: AppCommandError, /) -> None:
        content = f"Something went wrong when executing the command:\n```\n{error}\n```"

        if isinstance(error, errors.CommandSignatureMismatch):
            return

        with contextlib.suppress(InteractionResponded):
            await interaction.response.defer()

        await interaction.followup.send(content)

        logging.exception("We have gone under a crisis!!!", stack_info=True, exc_info=error)
