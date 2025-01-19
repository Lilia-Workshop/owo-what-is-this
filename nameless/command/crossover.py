import contextlib
import logging

import discord
import discord.ui
from discord.ext import commands
from prisma.models import CrossChatConnection, CrossChatMessage, CrossChatRoom

from nameless import Nameless
from nameless.custom.crud import NamelessPrisma

__all__ = ["CrossOverCommand"]

nameless_accepted_channels = discord.TextChannel | discord.Thread


class CrossOverCommand(commands.Cog):
    def __init__(self, bot: Nameless):
        self.bot: Nameless = bot

    async def _get_subscribed_channels(
        self, this_guild: discord.Guild, this_channel: nameless_accepted_channels
    ) -> list[tuple[CrossChatConnection, nameless_accepted_channels]]:
        """Get list of subscribed guild channels."""
        connections = await CrossChatConnection.prisma().find_many(
            where={"SourceGuildId": this_guild.id, "SourceChannelId": this_channel.id}
        )

        result: list[tuple[CrossChatConnection, nameless_accepted_channels]] = []

        for conn in connections:
            guild = self.bot.get_guild(conn.TargetGuildId)

            if guild is None:
                continue

            channel = guild.get_channel(conn.TargetChannelId)

            if channel is None:
                continue

            if isinstance(channel, nameless_accepted_channels):
                result.append((conn, channel))

        return result

    async def _get_subscribed_messages(
        self,
        this_guild: discord.Guild,
        this_channel: nameless_accepted_channels,
        this_message: discord.Message,
    ) -> list[tuple[CrossChatConnection, discord.Message]]:
        """Get subscribed messages."""
        connections = await CrossChatConnection.prisma().find_many(
            where={
                "SourceGuildId": this_guild.id,
                "SourceChannelId": this_channel.id,
                "Messages": {"some": {"OriginMessageId": this_message.id}},
            },
            include={"Messages": True},
        )

        result: list[tuple[CrossChatConnection, discord.Message]] = []

        for conn in connections:
            guild = self.bot.get_guild(conn.TargetGuildId)

            if guild is None:
                continue

            channel = guild.get_channel(conn.TargetChannelId)

            if channel is None:
                continue

            if not isinstance(channel, nameless_accepted_channels):
                continue

            assert conn.Messages is not None

            the_true_id: int = [
                x.ClonedMessageId for x in conn.Messages if x.OriginMessageId == this_message.id
            ][0]

            the_true_message = await channel.fetch_message(the_true_id)

            result.append((conn, the_true_message))

        return result

    async def _is_connected_to_each_other(
        self,
        this_guild: discord.Guild,
        this_channel: nameless_accepted_channels,
        that_guild: discord.Guild,
        that_channel: nameless_accepted_channels,
    ) -> bool:
        """Return if the 2 rooms are connected."""
        conn1 = await CrossChatConnection.prisma().find_first(
            where={
                "SourceGuildId": this_guild.id,
                "SourceChannelId": this_channel.id,
                "TargetGuildId": that_guild.id,
                "TargetChannelId": that_channel.id,
            }
        )

        conn2 = await CrossChatConnection.prisma().find_first(
            where={
                "SourceGuildId": that_guild.id,
                "SourceChannelId": that_channel.id,
                "TargetGuildId": this_guild.id,
                "TargetChannelId": this_channel.id,
            }
        )

        return not (conn1 is None and conn2 is None)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        assert message.guild is not None
        assert message.channel is not None
        assert self.bot.user is not None

        if message.author.id == self.bot.user.id:
            return

        if not isinstance(message.channel, nameless_accepted_channels):
            return

        for conn, channel in await self._get_subscribed_channels(message.guild, message.channel):
            embed = discord.Embed(description=message.content, color=discord.Colour.orange())

            avatar_url = message.author.avatar.url if message.author.avatar else ""
            guild_icon = message.guild.icon.url if message.guild.icon else ""

            embed.set_author(name=f"@{message.author.global_name} wrote:", icon_url=avatar_url)
            embed.set_footer(
                text=f"{message.guild.name} at #{message.channel.name}", icon_url=guild_icon
            )

            sent_message = await channel.send(
                embed=embed,
                stickers=message.stickers,
                files=[await x.to_file() for x in message.attachments],
            )

            await CrossChatMessage.prisma().create(
                data={
                    "Connection": {"connect": {"Id": conn.Id}},
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

        if not isinstance(message.channel, nameless_accepted_channels):
            return

        for _conn, the_message in await self._get_subscribed_messages(
            message.guild, message.channel, message
        ):
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

        if not isinstance(message.channel, nameless_accepted_channels):
            return

        for _conn, the_message in await self._get_subscribed_messages(
            message.guild, message.channel, message
        ):
            with contextlib.suppress(discord.NotFound):
                await the_message.delete()

    @commands.hybrid_group(fallback="code")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def crossover(self, ctx: commands.Context[Nameless]):
        """Establish this channel to the public."""
        await ctx.defer()

        assert ctx.guild is not None
        assert ctx.channel is not None

        if not isinstance(ctx.channel, nameless_accepted_channels):
            await ctx.send("You are not inside our accepted channel type (Text/Thread).")
            return

        await NamelessPrisma.get_guild_entry(ctx.guild)

        room_data: CrossChatRoom | None = await CrossChatRoom.prisma().find_first(
            where={"ChannelId": ctx.channel.id, "GuildId": ctx.guild.id},
        )

        if room_data is None:
            room_data = await CrossChatRoom.prisma().create(
                data={"GuildId": ctx.guild.id, "ChannelId": ctx.channel.id}
            )

        await ctx.send(f"Your cross-chat room code is: `{room_data.Id}`")

    @crossover.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def connect(
        self,
        ctx: commands.Context[Nameless],
        room_code: str = commands.parameter(description="Room code to connect to."),
    ):
        """Create link to another guild."""
        await ctx.defer()

        room_data: CrossChatRoom | None = await CrossChatRoom.prisma().find_first(
            where={"Id": room_code}
        )

        if room_data is None:
            await ctx.send("Room code does not exist!")
            return

        this_guild = ctx.guild
        that_guild = await ctx.bot.fetch_guild(room_data.GuildId)

        assert this_guild is not None
        assert that_guild is not None

        this_channel = ctx.channel
        that_channel = await ctx.bot.fetch_channel(room_data.ChannelId)

        assert this_channel is not None
        assert that_channel is not None

        if not isinstance(this_channel, nameless_accepted_channels):
            await ctx.send("You are not inside our accepted channel type (Text/Thread).")
            return

        assert isinstance(this_channel, nameless_accepted_channels)
        assert isinstance(that_channel, nameless_accepted_channels)

        if await self._is_connected_to_each_other(
            this_guild, this_channel, that_guild, that_channel
        ):
            await ctx.send("Already connected!")
            return

        if room_data.GuildId == this_guild.id and room_data.ChannelId == ctx.channel.id:
            await ctx.send("Don't connect to yourself!")
            return

        await NamelessPrisma.get_guild_entry(this_guild)
        await NamelessPrisma.get_guild_entry(that_guild)

        await CrossChatConnection.prisma().create(
            data={
                "RoomId": room_code,
                "SourceGuildId": this_guild.id,
                "SourceChannelId": this_channel.id,
                "TargetGuildId": that_guild.id,
                "TargetChannelId": that_channel.id,
            }
        )

        await this_channel.send("Linking success!")

        await CrossChatConnection.prisma().create(
            data={
                "RoomId": room_code,
                "SourceGuildId": that_guild.id,
                "SourceChannelId": that_channel.id,
                "TargetGuildId": this_guild.id,
                "TargetChannelId": this_channel.id,
            }
        )

        assert isinstance(this_channel.name, str)

        await that_channel.send(
            f"New connection comes from `#{this_channel.name}` at `{this_guild.name}`!"
        )

    @crossover.command()
    @commands.guild_only()
    @commands.has_guild_permissions()
    async def list(self, ctx: commands.Context[Nameless]):
        await ctx.defer()

        assert ctx.guild is not None
        assert ctx.channel is not None

        connections = await CrossChatConnection.prisma().find_many(
            where={
                "OR": [
                    {"SourceGuildId": ctx.guild.id, "SourceChannelId": ctx.channel.id},
                    {"TargetGuildId": ctx.guild.id, "TargetChannelId": ctx.channel.id},
                ]
            },
            distinct=["RoomId"],
        )

        embed = discord.Embed(
            description="All available connections, both in/outbound!",
            color=discord.Colour.orange(),
            title="Connection list",
        )

        rooms: list[str] = [conn.RoomId for conn in connections]

        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else "")
        embed.add_field(name="All connected rooms", value=f"`{"\n".join(rooms)}`")

        await ctx.send(
            embed=embed,
        )


async def setup(bot: Nameless):
    await bot.add_cog(CrossOverCommand(bot))
    logging.info("%s added!", __name__)


async def teardown(bot: Nameless):
    await bot.remove_cog(CrossOverCommand.__cog_name__)
    logging.warning("%s removed!", __name__)
