import discord
from prisma import Prisma, models
from prisma.errors import RecordNotFoundError

__all__ = ["NamelessCRUD"]

raw_db: Prisma = Prisma(auto_register=True)


class NamelessCRUD:
    """A repository class to connect to database."""

    @staticmethod
    async def init() -> None:
        await raw_db.connect()

    @staticmethod
    async def dispose() -> None:
        await raw_db.disconnect()

    @staticmethod
    async def get_or_create_guild_entry(
        guild: discord.Guild, *, include_cross_chat: bool = False
    ) -> models.Guild:
        try:
            return await raw_db.guild.find_first_or_raise(
                where={"Id": guild.id}, include={"CrossChat": include_cross_chat}
            )
        except RecordNotFoundError:
            return await raw_db.guild.create(
                data={"Id": guild.id}, include={"CrossChat": include_cross_chat}
            )
