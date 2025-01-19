from abc import ABC, abstractmethod
from collections.abc import Iterable

import discord
from discord.ui.button import Button
from discord.ui.view import View


class BaseView(View, ABC):
    @abstractmethod
    def add_pages(self, pages: Iterable[discord.Embed]):
        """
        Add multiple pages to the view.

        Parameters:
        -----------
        pages: Iterable[discord.Embed]
            An iterable of discord.Embed objects to add to the view.
        """
        pass

    @abstractmethod
    def add_button(self, button: Button["BaseView"]):
        """
        Add a button to the view.

        Parameters:
        -----------
        button: BaseButton
            The button to add to the view.
        """
        pass

    @abstractmethod
    async def next_page(self):
        """
        Go to the next page.
        """
        pass

    @abstractmethod
    async def previous_page(self):
        """
        Go to the previous page.
        """
        pass

    @abstractmethod
    async def go_to_first_page(self):
        """
        Go to the first page.
        """
        pass

    @abstractmethod
    async def go_to_last_page(self):
        """
        Go to the last page.
        """
        pass

    @abstractmethod
    async def go_to_page(self, page: int):
        """
        Go to a specific page.

        Parameters:
        -----------
        page: int
            The page number to go to.
        """
        pass

    @abstractmethod
    async def end(self):
        """
        End the view.
        """
        pass

    @abstractmethod
    async def start(self) -> bool:
        """
        Start the view. This method should be called
        after adding all the pages and buttons.

        This method will be blocking and wait for the view to finish interacting.

        Returns:
        --------
        bool:
            Return ``True`` if the view timed out, otherwise ``False``.
        """
        pass
