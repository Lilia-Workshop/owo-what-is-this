import logging

import discord
import discord.ui
from discord import app_commands
from discord.ext import commands
from prisma.models import CrossChatMessage, CrossChatSubscription

from nameless import Nameless
from nameless.custom.crud import NamelessCRUD
from nameless.custom.ui import NamelessYesNoPrompt

__all__ = ["CrossOverCommand"]


class CrossOverCommand(commands.GroupCog, group_name="crossover"):
    def __init__(self, bot: Nameless):
        self.bot: Nameless = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        assert message.guild is not None
        assert message.channel is not None
        assert self.bot.user is not None

        if message.author.id == self.bot.user.id:
            return

        if isinstance(message.channel, (discord.DMChannel, discord.PartialMessageable)):
            return

        subs = await CrossChatSubscription.prisma().find_many(
            where={"GuildId": message.guild.id, "ChannelId": message.channel.id}
        )

        for sub in subs:
            guild = self.bot.get_guild(sub.TargetGuildId)

            if guild is None:
                return

            channel = guild.get_channel(sub.TargetChannelId)

            if channel is None:
                return

            if isinstance(channel, (discord.ForumChannel, discord.CategoryChannel)):
                return

            embed = discord.Embed(
                description=message.content, color=discord.Colour.orange()
            )

            avatar_url = message.author.avatar.url if message.author.avatar else ""
            guild_icon = message.guild.icon.url if message.guild.icon else ""

            embed.set_author(
                name=f"@{message.author.global_name} wrote:", icon_url=avatar_url
            )
            embed.set_footer(
                text=f"{message.guild.name} at #{message.channel.name}",
                icon_url=guild_icon,
            )

            sent_message = await channel.send(
                embed=embed,
                stickers=message.stickers,
                files=[await x.to_file() for x in message.attachments],
            )

            await CrossChatMessage.prisma().create(
                data={
                    "Subscription": {"connect": {"SubscriptionId": sub.SubscriptionId}},
                    "OriginMessageId": message.id,
                    "ClonedMessageId": sent_message.id,
                }
            )

    @commands.Cog.listener()
    async def on_message_edit(self, _: discord.Message, message: discord.Message):
        assert message.guild is not None
        assert message.channel is not None
        assert self.bot.user is not None

        if message.author.id == self.bot.user.id:
            return

        if isinstance(message.channel, (discord.DMChannel, discord.PartialMessageable)):
            return

        subs = await CrossChatSubscription.prisma().find_many(
            where={
                "GuildId": message.guild.id,
                "ChannelId": message.channel.id,
                "Messages": {"some": {"OriginMessageId": message.id}},
            },
            include={"Messages": True},
        )

        for sub in subs:
            guild = self.bot.get_guild(sub.TargetGuildId)

            if guild is None:
                return

            channel = guild.get_channel(sub.TargetChannelId)

            if channel is None:
                return

            if isinstance(channel, (discord.ForumChannel, discord.CategoryChannel)):
                return

            assert sub.Messages is not None

            the_true_id: int = [
                x.ClonedMessageId
                for x in sub.Messages
                if x.OriginMessageId == message.id
            ][0]

            the_message: discord.Message = await channel.fetch_message(the_true_id)
            the_embed = the_message.embeds[0]
            the_embed.description = message.content

            await the_message.edit(embed=the_embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        assert message.guild is not None
        assert message.channel is not None
        assert self.bot.user is not None

        if message.author.id == self.bot.user.id:
            return

        if isinstance(message.channel, (discord.DMChannel, discord.PartialMessageable)):
            return

        subs = await CrossChatSubscription.prisma().find_many(
            where={
                "GuildId": message.guild.id,
                "ChannelId": message.channel.id,
                "Messages": {"some": {"OriginMessageId": message.id}},
            },
            include={"Messages": True},
        )

        for sub in subs:
            guild = self.bot.get_guild(sub.TargetGuildId)

            if guild is None:
                return

            channel = guild.get_channel(sub.TargetChannelId)

            if channel is None:
                return

            if isinstance(channel, (discord.ForumChannel, discord.CategoryChannel)):
                return

            assert sub.Messages is not None

            the_true_id: int = [
                x.ClonedMessageId
                for x in sub.Messages
                if x.OriginMessageId == message.id
            ][0]

            the_message: discord.Message = await channel.fetch_message(the_true_id)
            await the_message.delete()

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(
        target_guild="Target guild ID to establish.",
        target_channel="Target channel to establish.",
    )
    async def create_link(
        self,
        interaction: discord.Interaction[Nameless],
        target_guild: str,
        target_channel: str,
    ):
        """Create link to another guild."""
        await interaction.response.defer()

        guild = self.bot.get_guild(int(target_guild))

        if guild is None:
            await interaction.followup.send("That guild does not exist.")
            return

        channel = guild.get_channel(int(target_channel))

        if channel is None:
            await interaction.followup.send("That channel does not exist.")
            return

        if isinstance(channel, (discord.ForumChannel, discord.CategoryChannel)):
            await interaction.followup.send("Invalid channel to link to.")
            return

        assert interaction.guild is not None
        assert interaction.channel is not None

        temp_data: (
            CrossChatSubscription | None
        ) = await CrossChatSubscription.prisma().find_first(
            where={
                "ChannelId": interaction.channel.id,
                "TargetGuildId": guild.id,
                "TargetChannelId": channel.id,
            }
        )

        if temp_data is not None:
            await interaction.followup.send("You had a link with this place before.")
            return

        await interaction.followup.send("Sending out request, please wait.")

        prompt = NamelessYesNoPrompt()

        await channel.send("You have an incoming link!", view=prompt)
        await prompt.wait()

        if not prompt.is_a_yes:
            await interaction.followup.send("Response declined.")
            return

        await NamelessCRUD.get_or_create_guild_entry(interaction.guild)
        await NamelessCRUD.get_or_create_guild_entry(guild)

        await CrossChatSubscription.prisma().create(
            data={
                "Guild": {"connect": {"Id": interaction.guild.id}},
                "ChannelId": interaction.channel.id,
                "TargetGuildId": guild.id,
                "TargetChannelId": channel.id,
            }
        )

        await CrossChatSubscription.prisma().create(
            data={
                "Guild": {"connect": {"Id": guild.id}},
                "ChannelId": channel.id,
                "TargetGuildId": interaction.guild.id,
                "TargetChannelId": interaction.channel.id,
            }
        )

        await interaction.followup.send("Linking success!")


async def setup(bot: Nameless):
    await bot.add_cog(CrossOverCommand(bot))
    logging.info("%s added!", __name__)


async def teardown(bot: Nameless):
    await bot.remove_cog(CrossOverCommand.__cog_name__)
    logging.warning("%s removed!", __name__)
