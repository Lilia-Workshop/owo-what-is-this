import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Self, override

import discord
from discord import ActivityType, Permissions
from discord.app_commands import CommandTree
from discord.ext import commands

from nameless.config import nameless_config
from nameless.custom import NamelessCRUD

__all__ = ["Nameless"]


class Nameless(commands.Bot):
    """Customized Discord instance, or so called, nameless* bot."""

    def __init__(
        self,
        gateway_intents: discord.Intents,
        *args: object,
        tree_class: type[CommandTree[Self]],
        **kwargs: object,
    ):
        super().__init__(
            [],
            *args,
            intents=gateway_intents,
            tree_cls=tree_class,
            **kwargs,
        )
        self.description: str = nameless_config["nameless"]["description"]

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

        logging.info("nameless* is now operational!")
        nameless_config["nameless"]["start_time"] = datetime.now(timezone.utc)

    def start_bot(self, *, is_debug: bool = False) -> None:
        """Starts the bot."""
        logging.info(f"This bot will now start in {'debug' if is_debug else 'production'} mode.")
        self.run(os.getenv("TOKEN", ""), log_handler=None, root_logger=True)

    @override
    async def close(self) -> None:
        logging.warning("Shutting down...")
        await super().close()
        exit(0)

    @staticmethod
    def get_needed_permissions() -> Permissions:
        """Get minimum permissions needed for bare functionalities."""
        perms = Permissions.none()

        perms.view_channel = True
        perms.send_messages = True
        perms.send_messages_in_threads = True
        perms.embed_links = True
        perms.attach_files = True
        perms.use_external_emojis = True
        perms.use_external_stickers = True
        perms.connect = True
        perms.speak = True
        perms.use_voice_activation = True

        return perms

    async def _change_presence(self) -> None:
        """Set up nameless status."""
        await self.change_presence(
            status=discord.Status.do_not_disturb,
            activity=discord.Activity(type=ActivityType.watching, name="you"),
        )

    async def _register_commands(self) -> None:
        """Registers all available commands."""

        # We get ones that end in .py, in `command` directory.
        # And ignore ones that starts with _ (underscore)
        current_path = Path(__file__).parent
        py_file_re = re.compile(r"^(?!_.*)(\w.*).py")
        available_files = [*filter(py_file_re.match, os.listdir(current_path / "command"))]

        for file in available_files:
            module_name = file.replace(".py", "")
            module_name = f"nameless.command.{module_name}"
            await self.load_extension(module_name)
