from typing import Callable, Generic, TypeVar, override

import discord
from discord import ui

V = TypeVar("V", covariant=True)


class CustomInput(Generic[V], ui.TextInput[ui.Modal]):
    def __init__(
        self,
        label: str,
        custom_id: str,
        default: str = "0",
        convert: Callable[[str], V] = int,
    ) -> None:
        super().__init__(
            label=label, custom_id=custom_id, placeholder=default, default=default
        )
        self.convert: Callable[[str], V] = convert
        self.input: V = convert(default)

    @override
    async def callback(self, interaction: discord.Interaction):
        self.input = self.convert(self.value)
