import asyncio
import base64
import logging
import signal
from pathlib import Path

import aiohttp

from nameless.config import nameless_config

CWD = Path(__file__).parent
LAVALINK_URL = (
    "https://github.com/lavalink-devs/Lavalink/releases/latest/download/Lavalink.jar"
)
LAVALINK_BIN = CWD / "bin" / "Lavalink.jar"
LAVALINK_CONFIG = CWD / "bin" / "application.yml"

proc: asyncio.subprocess.Process | None = None
task: asyncio.Task[None] | None = None
stop_event = asyncio.Event()


async def start():
    """Start the Lavalink server from /bin folder."""
    global proc, stop_event
    while True:
        proc = await asyncio.create_subprocess_exec(
            "java", "-jar", "Lavalink.jar", cwd=CWD / "bin", stdout=-3
        )
        await proc.wait()
        if nameless_config["nameless"]["is_shutting_down"]:
            stop_event.set()
            break

        logging.warning("Lavalink server stopped. Restarting in 5 seconds...")
        await asyncio.sleep(5)


async def stop():
    """Stop the Lavalink server."""
    global proc, task, stop_event

    if proc:
        proc.send_signal(signal.CTRL_C_EVENT)
        await proc.wait()
        proc = None

    if task:
        await stop_event.wait()
        task.cancel()
        task = None


def check_file():
    """Check if the Lavalink.jar file exists."""
    try:
        with open(LAVALINK_BIN):
            return True
    except FileNotFoundError:
        return False


async def download_lavalink():
    """Download Lavalink.jar from the official repo."""
    LAVALINK_BIN.parent.mkdir(parents=True, exist_ok=True)
    async with aiohttp.ClientSession() as session, session.get(
        LAVALINK_URL, allow_redirects=True
    ) as resp:
        with open(LAVALINK_BIN, "wb") as f:
            f.write(await resp.read())


async def main(loop: asyncio.AbstractEventLoop):
    """Main function to start the Lavalink server."""
    global task

    if not check_file():
        logging.warning("Lavalink.jar not found. Downloading...")
        await download_lavalink()
    task = loop.create_task(start())
