from typing import Generic, TypeVar, override

import discord

from .custom_input import CustomInput

V = TypeVar("V", bound=type, covariant=True)


class BaseCustomModal(discord.ui.Modal, Generic[V]):
    def __init__(self, title: str) -> None:
        super().__init__(timeout=30, title=title)

    @override
    async def on_submit(self, interaction: discord.Interaction[discord.Client]) -> None:
        await interaction.response.defer()
        self.stop()

    def get_input(self) -> CustomInput[V]:
        return self.children[0]  # pyright: ignore[reportReturnType]

    @property
    def value(self) -> V:
        return self.get_input().input
