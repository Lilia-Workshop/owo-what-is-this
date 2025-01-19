# pyright: reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false
import discord
from discord import ui
from discord.ui import Button
from typing_extensions import override

from .base import BaseView

__all__ = ["ViewButton"]


class ToPageModal(discord.ui.Modal):
    page: ui.TextInput[BaseView] = ui.TextInput(label="Page")

    @override
    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.stop()

    def get_values(self):
        return self.page.value


class ViewButton(Button[BaseView]):
    NEXT_PAGE_ID: str = "0"
    PREVIOUS_PAGE_ID: str = "1"
    GO_TO_FIRST_PAGE_ID: str = "2"
    GO_TO_LAST_PAGE_ID: str = "3"
    GO_TO_PAGE_ID: str = "4"
    END_ID: str = "5"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._view: BaseView | None = None

    @override
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.view:
            raise ValueError("View not set for button")

        match self.custom_id:
            case self.NEXT_PAGE_ID:
                await self.view.next_page()
            case self.PREVIOUS_PAGE_ID:
                await self.view.previous_page()
            case self.GO_TO_FIRST_PAGE_ID:
                await self.view.go_to_first_page()
            case self.GO_TO_LAST_PAGE_ID:
                await self.view.go_to_last_page()
            case self.GO_TO_PAGE_ID:
                modal = ToPageModal()
                await interaction.response.send_modal(modal)
                if await modal.wait():
                    return

                if modal.page.value:
                    await self.view.go_to_page(int(modal.page.value) - 1)

            case self.END_ID:
                await self.view.end()
            case _:
                raise ValueError("Invalid button")

    @classmethod
    def create_button(
        cls,
        label: str | None,
        custom_id: str | None,
        emoji: discord.Emoji | discord.PartialEmoji | str | None,
        with_label: bool,
        with_emote: bool,
        with_disabled: bool,
        **kwargs,
    ):
        return cls(
            style=discord.ButtonStyle.gray,
            label=label if with_label else None,
            custom_id=custom_id,
            emoji=emoji if with_emote else None,
            disabled=with_disabled,
            **kwargs,
        )

    @classmethod
    def back(
        cls,
        with_label: bool = False,
        with_emote: bool = True,
        with_disabled: bool = False,
        **kwargs,
    ):
        return cls.create_button(
            "Back", cls.PREVIOUS_PAGE_ID, "⬅️", with_label, with_emote, with_disabled, **kwargs
        )

    @classmethod
    def next(
        cls,
        with_label: bool = False,
        with_emote: bool = True,
        with_disabled: bool = False,
        **kwargs,
    ):
        return cls.create_button(
            "Next", cls.NEXT_PAGE_ID, "➡️", with_label, with_emote, with_disabled, **kwargs
        )

    @classmethod
    def go_to_first_page(
        cls,
        with_label: bool = False,
        with_emote: bool = True,
        with_disabled: bool = False,
        **kwargs,
    ):
        return cls.create_button(
            "First Page",
            cls.GO_TO_FIRST_PAGE_ID,
            "⏮️",
            with_label,
            with_emote,
            with_disabled,
            **kwargs,
        )

    @classmethod
    def go_to_last_page(
        cls,
        with_label: bool = False,
        with_emote: bool = True,
        with_disabled: bool = False,
        **kwargs,
    ):
        return cls.create_button(
            "Last Page",
            cls.GO_TO_LAST_PAGE_ID,
            "⏭️",
            with_label,
            with_emote,
            with_disabled,
            **kwargs,
        )

    @classmethod
    def go_to_page(
        cls,
        with_label: bool = False,
        with_emote: bool = True,
        with_disabled: bool = False,
        **kwargs,
    ):
        return cls.create_button(
            "Page Selection",
            cls.GO_TO_PAGE_ID,
            "🔢",
            with_label,
            with_emote,
            with_disabled,
            **kwargs,
        )

    @classmethod
    def end(
        cls,
        with_label: bool = False,
        with_emote: bool = True,
        with_disabled: bool = False,
        **kwargs,
    ):
        return cls.create_button(
            "End", cls.END_ID, "⏹️", with_label, with_emote, with_disabled, **kwargs
        )
