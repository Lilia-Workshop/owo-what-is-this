import logging
import os
from typing import override

import discord
from discord import ActivityType, Permissions
from discord.ext import commands

from .config import nameless_config

__all__ = ["Nameless"]


class Nameless(commands.Bot):
    """Customized Discord instance, or so called, nameless* bot."""

    def __init__(self, *args: object, **kwargs: object):
        super().__init__([], *args, **kwargs)
        self.description = nameless_config["nameless"]["description"]

    @override
    async def setup_hook(self) -> None:
        logging.info("Registering commands.")
        await self._register_commands()

        logging.info("Syncing commands.")
        await self.tree.sync()
        logging.warning("Please wait at least one hour before using global commands.")

    async def on_ready(self):
        logging.info("Setting presence.")
        await self._change_presence()

        assert self.user is not None
        logging.info("Logged in as %s (ID: %s)", str(self.user), self.user.id)

    def start_bot(self, *, is_debug: bool = False) -> None:
        """Starts the bot."""
        logging.info(f"This bot will now start in {'debug' if is_debug else 'production'} mode.")
        self.run(os.getenv("TOKEN", ""), log_handler=None, root_logger=True)

    @override
    async def close(self) -> None:
        logging.warning("Shutting down...")
        await super().close()

    @staticmethod
    def get_needed_permissions() -> Permissions:
        """Get minimum permissions needed for bare functionalities."""
        return Permissions(
            view_channel=True,
            send_messages=True,
            send_messages_in_threads=True,
            manage_channels=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            use_external_emojis=True,
            use_external_stickers=True,
            add_reactions=True,
            connect=True,
            speak=True,
            use_voice_activation=True,
        )

    async def _change_presence(self) -> None:
        """Set up nameless status."""
        await self.change_presence(
            status=discord.Status.do_not_disturb, activity=discord.Activity(type=ActivityType.watching, name="you")
        )

    async def _register_commands(self) -> None:
        """Registers all commands."""
        ...
