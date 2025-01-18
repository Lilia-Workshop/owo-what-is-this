import logging

import discord
import discord.ui
from discord import app_commands
from discord.ext import commands
from prisma.models import CrossChatMessage, CrossChatRoom, CrossChatSubscription

from nameless import Nameless
from nameless.custom.crud import NamelessCRUD

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
            where={"GuildId": message.guild.id, "ChannelId": message.channel.id},
            include={"Room": True},
        )

        for sub in subs:
            assert sub.Room is not None

            guild = self.bot.get_guild(sub.Room.GuildId)

            if guild is None:
                return

            channel = guild.get_channel(sub.Room.ChannelId)

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
            include={"Messages": True, "Room": True},
        )

        for sub in subs:
            assert sub.Room is not None

            guild = self.bot.get_guild(sub.Room.GuildId)

            if guild is None:
                return

            channel = guild.get_channel(sub.Room.ChannelId)

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
            include={"Messages": True, "Room": True},
        )

        for sub in subs:
            assert sub.Room is not None

            guild = self.bot.get_guild(sub.Room.GuildId)

            if guild is None:
                return

            channel = guild.get_channel(sub.Room.ChannelId)

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
    @app_commands.checks.has_permissions(manage_guild=True)
    async def publish(self, interaction: discord.Interaction[Nameless]):
        """Establish this channel to the public."""
        await interaction.response.defer()

        assert interaction.guild is not None
        assert interaction.channel is not None

        room_data: CrossChatRoom | None = await CrossChatRoom.prisma().find_first(
            where={"ChannelId": interaction.channel.id, "GuildId": interaction.guild.id}
        )

        if room_data is None:
            room_data = await CrossChatRoom.prisma().create(
                data={
                    "GuildId": interaction.guild.id,
                    "ChannelId": interaction.channel.id,
                }
            )

        await interaction.followup.send(
            f"Your cross-chat room code is: `{room_data.RoomId}`"
        )

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(room_code="Room code to subscribe.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def connect(self, interaction: discord.Interaction[Nameless], room_code: str):
        """Create link to another guild."""
        await interaction.response.defer()

        room_data: CrossChatRoom | None = await CrossChatRoom.prisma().find_first(
            where={"RoomId": room_code}
        )

        if room_data is None:
            await interaction.followup.send("Room code does not exist!")
            return

        assert interaction.guild is not None
        assert interaction.channel is not None

        this_guild = interaction.guild
        that_guild = await self.bot.fetch_guild(room_data.GuildId)

        assert this_guild is not None
        assert that_guild is not None

        if (
            room_data.GuildId == this_guild.id
            and room_data.ChannelId == interaction.channel.id
        ):
            await interaction.followup.send("Don't connect to yourself!")
            return

        await NamelessCRUD.get_or_create_guild_entry(this_guild)
        await NamelessCRUD.get_or_create_guild_entry(that_guild)

        await CrossChatSubscription.prisma().create(
            data={
                "Guild": {"connect": {"Id": this_guild.id}},
                "ChannelId": interaction.channel.id,
                "Room": {"connect": {"RoomId": room_code}},
            }
        )

        await interaction.followup.send(
            "Linking success! Please note that the other guild need to do the same."
        )


async def setup(bot: Nameless):
    await bot.add_cog(CrossOverCommand(bot))
    logging.info("%s added!", __name__)


async def teardown(bot: Nameless):
    await bot.remove_cog(CrossOverCommand.__cog_name__)
    logging.warning("%s removed!", __name__)
