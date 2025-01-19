from collections.abc import Iterable
from typing import final, override

import discord
from discord.ext import commands
from discord.ui import Button

from nameless import Nameless

from .base import BaseView

__all__ = ["ViewMenu"]


@final
class ViewMenu(BaseView):
    def __init__(self, ctx: commands.Context[Nameless], timeout: int = 60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.pages: list[discord.Embed] = []
        self.current_page = 0
        self._current_message: discord.Message | None = None

    @property
    def message(self):
        if not self._current_message:
            return self.ctx.message

        return self._current_message

    @message.setter
    def message(self, value: discord.Message):
        self._current_message = value

    @override
    def add_pages(self, pages: Iterable[discord.Embed]):
        self.pages.extend(pages)

    @override
    def add_button(self, button: Button[BaseView]):
        self.add_item(button)

    @override
    async def next_page(self):
        if self.current_page + 1 >= len(self.pages):
            self.current_page = 0
        else:
            self.current_page += 1
        await self.message.edit(embed=self.pages[self.current_page], view=self)

    @override
    async def previous_page(self):
        if self.current_page - 1 < 0:
            self.current_page = len(self.pages) - 1
        else:
            self.current_page -= 1
        await self.message.edit(embed=self.pages[self.current_page], view=self)

    @override
    async def go_to_first_page(self):
        await self.message.edit(embed=self.pages[0], view=self)

    @override
    async def go_to_last_page(self):
        await self.message.edit(embed=self.pages[-1], view=self)

    @override
    async def go_to_page(self, page: int):
        self.current_page = page
        await self.ctx.send(embed=self.pages[self.current_page], view=self)

    @override
    async def end(self):
        self.stop()
        # await self.__current_message.delete()
        await self.message.edit(view=None)

    @override
    async def start(self):
        self.message = await self.ctx.send(embed=self.pages[0], view=self)
        return await self.wait()
