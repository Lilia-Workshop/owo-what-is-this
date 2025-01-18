from typing import Generic, TypeVar, override

import discord
from discord import ui

V = TypeVar("V", bound=type, covariant=True)


class CustomInput(ui.TextInput[ui.Modal], Generic[V]):
    def __init__(
        self, label: str, custom_id: str, default: str = "0", convert: V = str
    ) -> None:
        super().__init__(
            label=label, custom_id=custom_id, placeholder=default, default=default
        )
        self.convert: V = convert
        self.input: V = convert(default)

    @override
    async def callback(self, interaction: discord.Interaction):
        self.input = self.convert(self.value)
