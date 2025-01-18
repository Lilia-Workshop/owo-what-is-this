from typing import cast, override

import discord

from nameless.custom.ui import CustomDropdown


class BaseView(discord.ui.View):
    def __init__(self, author: discord.Member | discord.User, message: discord.Message):
        super().__init__(timeout=30)
        self.author: discord.Member | discord.User = author
        self.message: discord.Message = message

    @override
    async def interaction_check(
        self, interaction: discord.Interaction[discord.Client]
    ) -> bool:
        return interaction.user == self.author

    def get_dropdown(self) -> CustomDropdown:
        return cast(CustomDropdown, self.children[0])
