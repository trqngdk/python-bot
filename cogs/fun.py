import random
from typing import Final
from dataclasses import dataclass
import discord

from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from requests_cache import CachedSession
from helpers import checks

GREEN_COLOR = 0x72b01d  # Used to be 0x9C84EF
RED_COLOR = 0xb01d1f  # Used to be 0xE02B2B


class Choice(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Heads", style=discord.ButtonStyle.blurple)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.value = "heads"
        self.stop()

    @discord.ui.button(label="Tails", style=discord.ButtonStyle.blurple)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "tails"
        self.stop()


class RockPaperScissors(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Scissors", description="You choose scissors.", emoji="✂"
            ),
            discord.SelectOption(
                label="Rock", description="You choose rock.", emoji="🪨"
            ),
            discord.SelectOption(
                label="paper", description="You choose paper.", emoji="🧻"
            ),
        ]
        super().__init__(
            placeholder="Choose...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        choices = {
            "rock": 0,
            "paper": 1,
            "scissors": 2,
        }
        user_choice = self.values[0].lower()
        user_choice_index = choices[user_choice]

        bot_choice = random.choice(list(choices.keys()))
        bot_choice_index = choices[bot_choice]

        result_embed = discord.Embed(color=GREEN_COLOR)
        result_embed.set_author(
            name=interaction.user, icon_url=interaction.user.avatar.url
        )

        if user_choice_index == bot_choice_index:
            result_embed.description = f"**That's a draw!**\nYou've chosen \
                {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0xF59E42

        elif user_choice_index == 0 and bot_choice_index == 2:
            result_embed.description = f"**You won!**\nYou've chosen \
                {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = GREEN_COLOR

        elif user_choice_index == 1 and bot_choice_index == 0:
            result_embed.description = f"**You won!**\nYou've chosen \
                {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = GREEN_COLOR

        elif user_choice_index == 2 and bot_choice_index == 1:
            result_embed.description = f"**You won!**\nYou've chosen \
                {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = GREEN_COLOR

        else:
            result_embed.description = (
                f"**I won!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            )
            result_embed.colour = RED_COLOR
        await interaction.response.edit_message(
            embed=result_embed, content=None, view=None
        )


class RockPaperScissorsView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(RockPaperScissors())


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="randomfact", description="Get a random fact.")
    @checks.not_blacklisted()
    async def randomfact(self, context: Context) -> None:
        """
        Get a random fact.

        :param context: The hybrid command context.
        """

        url: Final = 'https://uselessfacts.jsph.pl/random.json?language=en'

        session = CachedSession(
            cache_name='cache/fact_cache',
            expire_after=1
        )

        @dataclass
        class Text:
            id: str = None
            text: str = None
            source: str = None
            source_url: str = None
            language: str = None
            permalink: str = None

        response = session.get(url)

        try:
            json: dict = response.json()
            text = Text(**json)

            embed = discord.Embed(
                description=text.text, color=GREEN_COLOR)
            await context.send(embed=embed)

        except ImportError as error:
            embed = discord.Embed(
                title="Error!",
                description=f"{response.status_code} - {error}",
                color=RED_COLOR,
            )
            await context.send(embed=embed)

    @commands.hybrid_command(name="dog", description="Get a dog image.")
    @checks.not_blacklisted()
    async def dog(self, context: Context) -> None:
        """
        Get a dog image.

        :param context: The hybrid command context.
        """

        url: Final = 'https://dog.ceo/api/breeds/image/random'

        session = CachedSession(
            cache_name='cache/dog_cache',
            expire_after=1
        )

        @dataclass
        class Picture:
            message: str = None
            status: str = None

        response = session.get(url)

        try:
            json: dict = response.json()
            message = Picture(**json)

            embed = discord.Embed(title="Woof Woof!", color=GREEN_COLOR)
            embed.set_image(url=message.message)
            await context.send(embed=embed)

        except ImportError as error:
            embed = discord.Embed(
                title="Error!",
                description=f"{response.status_code} - {error}",
                color=RED_COLOR,
            )
            await context.send(embed=embed)

    @commands.hybrid_command(name="cat", description="Get a cat image")
    @checks.not_blacklisted()
    @app_commands.describe(word="Provide a word.", size="Provide size of the image.")
    async def cat(self, context: Context, *, word: str, size: int) -> None:
        """
        Get a cat image.

        :param context: The hybrid command context.
        :param word: The text that will be displayed on the image.
        :param size: The size of the image.
        """

        embed = discord.Embed(title="Meow", color=GREEN_COLOR)
        embed.set_image(url=f"https://cataas.com/cat/says/{word}?size={size}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="coinflip", description="Make a coin flip, but give your bet before."
    )
    @checks.not_blacklisted()
    async def coinflip(self, context: Context) -> None:
        """
        Make a coin flip, but give your bet before.

        :param context: The hybrid command context.
        """

        buttons = Choice()
        embed = discord.Embed(
            description="What is your bet?", color=GREEN_COLOR)
        message = await context.send(embed=embed, view=buttons)
        await buttons.wait()  # We wait for the user to click a button.
        result = random.choice(["heads", "tails"])

        if buttons.value == result:
            embed = discord.Embed(
                description=f"Correct! You guessed `{buttons.value}` and \
                    I flipped the coin to `{result}`.",
                color=GREEN_COLOR,
            )

        else:
            embed = discord.Embed(
                description=f"Woops! You guessed `{buttons.value}` and \
                    I flipped the coin to `{result}`, better luck next time!",
                color=RED_COLOR,
            )
        await message.edit(embed=embed, view=None, content=None)

    @commands.hybrid_command(
        name="rps", description="Play the rock paper scissors game against the bot."
    )
    @checks.not_blacklisted()
    async def rock_paper_scissors(self, context: Context) -> None:
        """
        Play the rock paper scissors game against the bot.

        :param context: The hybrid command context.
        """

        view = RockPaperScissorsView()
        await context.send("Please make your choice", view=view)


async def setup(bot):
    await bot.add_cog(Fun(bot))
