import logging
import os
import sys

import discord
from dotenv import load_dotenv

from nameless.custom import command_tree
from nameless.genesis import Nameless

load_dotenv()

is_debug: bool = bool(int(os.getenv("DEBUG", 0)))

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] [%(name)s] %(message)s",
    stream=sys.stdout,
    level=logging.DEBUG if is_debug else logging.INFO,
)

logging.getLogger().name = "nameless"

intents = discord.Intents.all()

nameless = Nameless(
    intents=intents,
    tree_cls=command_tree.NamelessCommandTree,
)

nameless.start_bot(is_debug=is_debug)
