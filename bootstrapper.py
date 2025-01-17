import logging
import os
import sys

import discord
from discord.ext.commands import when_mentioned_or
from dotenv import load_dotenv

from nameless import Nameless
from nameless.custom import command_tree

load_dotenv()

is_debug: bool = bool(int(os.getenv("DEBUG", 0)))

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] [%(name)s] %(message)s",
    stream=sys.stdout,
    level=logging.DEBUG if is_debug else logging.INFO,
)

logging.getLogger().name = "nameless"

intents = discord.Intents.default()
intents.message_content = True

nameless = Nameless(
    command_prefix=when_mentioned_or("nl."),
    gateway_intents=intents,
    tree_class=command_tree.NamelessCommandTree,
)

nameless.start_bot(is_debug=is_debug)
