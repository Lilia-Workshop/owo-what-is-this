import logging
from datetime import datetime
from platform import python_version
from typing import cast

import discord
from discord import NotFound, app_commands
from discord.ext import commands

from nameless import Nameless
from nameless.config import nameless_config

__all__ = ["GeneralCommand"]


class GeneralCommand(commands.Cog):
    def __init__(self, bot: Nameless) -> None:
        super().__init__()
        self.bot: Nameless = bot

    @app_commands.command()
    @app_commands.describe(member="A member, default to you.")
    async def user(
        self, interaction: discord.Interaction[Nameless], member: discord.Member | None
    ):
        """View someone's information."""
        await interaction.response.defer()

        member = member if member else cast(discord.Member, interaction.user)

        account_create_date = member.created_at
        join_date = member.joined_at

        assert join_date is not None

        flags = [
            flag.replace("_", " ").title() for flag, has in member.public_flags if has
        ]
        embed: discord.Embed = (
            discord.Embed(
                description=f"Public handle: `@{member.name}`",
                timestamp=datetime.now(),
                title=f"@{member.display_name} - "
                + ("[👑]" if member.guild.owner == member else "[😎]")
                + ("[🤖]" if member.bot else ""),
                color=discord.Color.orange(),
            )
            .set_thumbnail(url=member.display_avatar.url)
            .add_field(name="ℹ️ User ID", value=f"{member.id}")
            .add_field(
                name="📆 Account created since",
                value=f"<t:{int(account_create_date.timestamp())}:R>",
            )
            .add_field(
                name="🤝 Membership since", value=f"<t:{int(join_date.timestamp())}:R>"
            )
            .add_field(
                name="🌟 Badges",
                value=", ".join(flags) if flags else "None",
                inline=False,
            )
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    async def guild(self, interaction: discord.Interaction[Nameless]):
        """View this guild's information"""
        await interaction.response.defer()

        guild = interaction.guild

        assert guild is not None
        assert guild.owner is not None  # how the fuck can a guild has no owner?

        guild_create_date = guild.created_at
        members = guild.members

        bots_count = len([member for member in members if member.bot])
        humans_count = len([member for member in members if not member.bot])
        total_count = bots_count + humans_count
        public_threads_count = len([thread for thread in guild.threads])
        events = guild.scheduled_events
        boosts_count = guild.premium_subscription_count

        embed = (
            discord.Embed(
                description=f"Owner: {guild.owner.mention}",
                timestamp=datetime.now(),
                title=guild.name,
                color=discord.Color.orange(),
            )
            .set_thumbnail(url=guild.icon.url if guild.icon else "")
            .add_field(name="ℹ️ Guild ID", value=f"{guild.id}")
            .add_field(
                name="⏰ Creation date",
                value=f"<t:{int(guild_create_date.timestamp())}:f>",
            )
            .add_field(
                name=f"👋 Headcount: {total_count}",
                value=f"BOT: {bots_count}, Human: {humans_count}",
            )
            .add_field(
                name="💬 Channels",
                value=(
                    f"{len(guild.channels)} channel(s) - "
                    + f"{public_threads_count} thread(s)"
                ),
            )
            .add_field(name="⭐ Roles", value=f"{len(guild.roles)}")
            .add_field(name="📆 Events", value=f"{len(events)}")
            .add_field(name="⬆️ Boosts", value=f"{boosts_count} boost(s)")
            .set_image(url=guild.banner.url if guild.banner else "")
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command()
    async def nameless(self, interaction: discord.Interaction[Nameless]):
        """So, you would like to know me?"""
        await interaction.response.defer()

        assert interaction.client.application is not None
        assert interaction.client.user is not None

        servers_count = len(interaction.client.guilds)
        total_members_count = sum(
            len(guild.members) for guild in interaction.client.guilds
        )

        launch_time: datetime = nameless_config["nameless"]["start_time"]

        uptime = int(launch_time.timestamp())
        bot_inv = discord.utils.oauth_url(
            interaction.client.user.id,
            permissions=self.bot.get_needed_permissions(),
            scopes=["bot", "applications.commands"],
        )
        support_guild: str = nameless_config["nameless"]["support_server"]

        try:
            if support_guild:
                inv = await self.bot.fetch_invite(support_guild)
                support_guild = inv.url
        except NotFound:
            support_guild = ""

        embed: discord.Embed = (
            discord.Embed(
                title="So... you would like to know me, right 😳",
                color=discord.Color.orange(),
                timestamp=datetime.now(),
                description="*Not much thing, I guess.*",
            )
            .set_thumbnail(url=interaction.client.user.display_avatar.url)
            .add_field(name="⭐ Biography", value=self.bot.description, inline=False)
            .add_field(
                name="🫡 Service status",
                value=(
                    f"Serving {servers_count} servers "
                    + f"and {total_members_count} users."
                ),
                inline=False,
            )
            .add_field(
                name="👋 Online since",
                value=f"<t:{uptime}:F> (<t:{uptime}:R>)",
                inline=False,
            )
            .add_field(name="ℹ️ Version", value=nameless_config["nameless"]["version"])
            .add_field(
                name="💻 Runtime",
                value=(
                    f"**discord.py {discord.__version__}** "
                    + f"on **Python {python_version()}**"
                ),
            )
        )

        buttons = discord.ui.View()

        if interaction.client.application.bot_public:
            buttons.add_item(
                discord.ui.Button(
                    label="Invite me!",
                    style=discord.ButtonStyle.url,
                    url=bot_inv,
                    emoji="😳",
                )
            )

        if bool(support_guild):
            buttons.add_item(
                discord.ui.Button(
                    label="Support server",
                    style=discord.ButtonStyle.url,
                    url=support_guild,
                    emoji="🤝",
                )
            )

        buttons.add_item(
            discord.ui.Button(
                label="Source code",
                style=discord.ButtonStyle.url,
                url="https://github.com/team-nameless/nameless-discord-bot",
                emoji="📃",
            )
        )

        await interaction.followup.send(embed=embed, view=buttons)


async def setup(bot: Nameless):
    await bot.add_cog(GeneralCommand(bot))
    logging.info("%s added!", __name__)


async def teardown(bot: Nameless):
    await bot.remove_cog(GeneralCommand.__cog_name__)
    logging.warning("%s removed!", __name__)
