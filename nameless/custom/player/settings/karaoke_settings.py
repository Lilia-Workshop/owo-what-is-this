# pyright: reportAny=false, reportExplicitAny=false

import logging
from enum import Enum
from typing import Any, TypedDict, cast, override

import discord
from discord.ext import commands

from nameless import Nameless
from nameless.custom.ui import CustomDropdown
from nameless.custom.ui.modal import BaseCustomModal, CustomInput

from .base import BaseView


class KaraokeFlags(Enum):
    LEVEL = "0"
    MONO_LEVEL = "1"
    FILTER_BAND = "2"
    FILTER_WIDTH = "3"


class LevelView(BaseCustomModal[int]):
    def __init__(self, title: str):
        super().__init__(title)
        self.add_item(
            CustomInput(
                label="Level", custom_id="level_input", default="0", convert=int
            )
        )


class MonoLevelView(BaseCustomModal[int]):
    def __init__(self, title: str):
        super().__init__(title)
        self.add_item(
            CustomInput(
                label="Mono Level",
                custom_id="mono_level_input",
                default="0",
                convert=int,
            )
        )


class FilterBandView(BaseCustomModal[int]):
    def __init__(self, title: str):
        super().__init__(title)
        self.add_item(
            CustomInput(
                label="Filter Band",
                custom_id="filter_band_input",
                default="0",
                convert=int,
            )
        )


class FilterWidthView(BaseCustomModal[int]):
    def __init__(self, title: str):
        super().__init__(title)
        self.add_item(
            CustomInput(
                label="Filter Width",
                custom_id="filter_width_input",
                default="0",
                convert=int,
            )
        )


class OptionsType(TypedDict):
    view_class: type[BaseCustomModal[int | str | None]]
    title: str
    description: str
    message: str


OPTION_MAPPING: dict[KaraokeFlags, OptionsType] = {
    KaraokeFlags.LEVEL: {
        "view_class": LevelView,
        "title": "Karaoke Level",
        "description": "Enter a new level",
        "message": "Level set to {value}",
    },
    KaraokeFlags.MONO_LEVEL: {
        "view_class": MonoLevelView,
        "title": "Karaoke Mono Level",
        "description": "Enter a new mono level",
        "message": "Mono level set to {value}",
    },
    KaraokeFlags.FILTER_BAND: {
        "view_class": FilterBandView,
        "title": "Karaoke Filter Band",
        "description": "Enter a new filter band",
        "message": "Filter band set to {value}",
    },
    KaraokeFlags.FILTER_WIDTH: {
        "view_class": FilterWidthView,
        "title": "Karaoke Filter Width",
        "description": "Enter a new filter width",
        "message": "Filter width set to {value}",
    },
}


class KaraokeSettingDropdown(CustomDropdown):
    def __init__(self):
        super().__init__(custom_id="karaoke_dropdown", placeholder="Select a setting")
        self.add_option(label="Level", value=str(KaraokeFlags.LEVEL.value))
        self.add_option(label="Mono Level", value=str(KaraokeFlags.MONO_LEVEL.value))
        self.add_option(label="Filter Band", value=str(KaraokeFlags.FILTER_BAND.value))
        self.add_option(
            label="Filter Width", value=str(KaraokeFlags.FILTER_WIDTH.value)
        )

        self._modal: BaseCustomModal[int | str | None] | None = None
        self._output_message: str | None = None

    def get_selected_flag(self) -> KaraokeFlags:
        return KaraokeFlags(self.values[0])

    def get_field_index(self) -> int:
        return int(self.get_selected_flag().value)

    @property
    def output_message(self) -> str:
        if not self._output_message:
            return "No message"
        return self._output_message

    @property
    def input_value(self) -> Any:
        if not self._modal:
            return None
        return self._modal.value

    @override
    async def callback(self, interaction: discord.Interaction[discord.Client]):
        selected_flag = self.get_selected_flag()
        option = OPTION_MAPPING.get(selected_flag)

        if not option:
            return await interaction.response.send_message("Invalid option selected")

        view_class = option["view_class"]
        title = option["title"]
        self._output_message = option["message"]

        self._modal = view_class(title=title)
        await interaction.response.send_modal(self._modal)
        if await self._modal.wait():
            return

        if self.view is not None:
            self.view.stop()


class KaraokeSettingView(BaseView):
    def __init__(self, author: discord.Member | discord.User, message: discord.Message):
        super().__init__(author, message)
        self.add_item(KaraokeSettingDropdown())

    @override
    def get_dropdown(self) -> KaraokeSettingDropdown:
        return cast(KaraokeSettingDropdown, self.children[0])  # type: ignore


async def make(ctx: commands.Context[Nameless], message: discord.Message):
    embed = (
        discord.Embed(
            title="Karaoke Settings",
            description="Select a setting to change",
            color=discord.Color.blurple(),
        )
        .add_field(
            name="Level", value="Change the level of the karaoke effect", inline=False
        )
        .add_field(
            name="Mono Level",
            value="Change the mono level of the karaoke effect",
            inline=False,
        )
        .add_field(
            name="Filter Band",
            value="Change the filter band of the karaoke effect",
            inline=False,
        )
        .add_field(
            name="Filter Width",
            value="Change the filter width of the karaoke effect",
            inline=False,
        )
    )

    while True:
        view = KaraokeSettingView(ctx.author, message)
        await message.edit(view=view, embed=embed)

        if await view.wait():
            await message.edit(view=None)
            return

        logging.error(view.get_dropdown().input_value)
