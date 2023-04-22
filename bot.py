import asyncio
import json
import logging
import os
import platform
import random
import sys
import aiosqlite
import discord

from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
import exceptions

RED_COLOR = 0xb01d1f  # Used to be 0xE02B2B

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")

else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json",
              encoding="utf-8") as file:
        config = json.load(file)


# https://discordpy.readthedocs.io/en/latest/intents.html
# https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents
intents = discord.Intents.default()

# Uncomment this if you want to use normal (prefix) commands.
# Make sure to enable this intent in Discord Developer Portal too!
# But it is still recommended to use slash commands!
# intents.message_content = True

bot = Bot(
    command_prefix=commands.when_mentioned_or(config["prefix"]),
    intents=intents,
    help_command=None,
)

# Setup both of the loggers


class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) \
            (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())

# File handler
file_handler = logging.FileHandler(
    filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)
bot.logger = logger


async def init_database():
    async with aiosqlite.connect(
        f"{os.path.realpath(os.path.dirname(__file__))}/database/database.database"
    ) as database:
        with open(
            f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql", encoding="utf-8"
        ) as sqlite_file:
            await database.executescript(sqlite_file.read())
        await database.commit()

bot.config = config


@bot.event
async def on_ready() -> None:
    """
    The code in this event is executed when the bot is ready.
    """

    bot.logger.info("Logged in as %s", bot.user.name)
    bot.logger.info("discord.py API version: %s", discord.__version__)
    bot.logger.info("Python version: %s", platform.python_version())
    bot.logger.info("Running on: %s %s (%s)", platform.system(),
                    platform.release(), os.name)
    bot.logger.info("-------------------")
    status_task.start()

    if config["sync_commands_globally"]:
        bot.logger.info("Syncing commands globally...")
        await bot.tree.sync()


@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """
    Setup the game status of the bot.
    """

    status = ["by trqngdk"]
    await bot.change_presence(activity=discord.Game(random.choice(status)))


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    The code in this event is executed every time
    someone sends a message, with or without the prefix

    :param message: The message that was sent.
    """

    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)


@bot.event
async def on_command_completion(context: Context) -> None:
    """
    The code in this event is executed every time a normal command has been *successfully* executed.

    :param context: The context of the command that has been executed.
    """

    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])

    if context.guild is not None:
        bot.logger.info(
            f"Executed {executed_command} command in \
                {context.guild.name} (ID: {context.guild.id}) \
                    by {context.author} (ID: {context.author.id})"
        )

    else:
        bot.logger.info(
            f"Executed {executed_command} command \
                by {context.author} (ID: {context.author.id}) in DMs"
        )


@bot.event
async def on_command_error(context: Context, error) -> None:
    """
    The code in this event is executed every time a normal valid command catches an error.

    :param context: The context of the normal command that failed executing.
    :param error: The error that has been faced.
    """

    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            description=f"**Please slow down** - \
                You can use this command again in \
                    {f'{round(hours)} hours' if round(hours) > 0 else ''} \
                    {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} \
                        {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=RED_COLOR,
        )
        await context.send(embed=embed)

    elif isinstance(error, exceptions.UserBlacklisted):

        # The code here will only execute if the error is an instance of 'UserBlacklisted',
        # which can occur when using the @checks.not_blacklisted() check in your command,
        # or you can raise the error by yourself.
        embed = discord.Embed(
            description="You are blacklisted from using the bot!", color=RED_COLOR
        )
        await context.send(embed=embed)

        if context.guild:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) \
                    tried to execute a command in the guild {context.guild.name} \
                        (ID: {context.guild.id}), but the user is blacklisted from using the bot."
            )

        else:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) \
                    tried to execute a command in the bot's DMs, \
                        but the user is blacklisted from using the bot."
            )

    elif isinstance(error, exceptions.UserNotOwner):
        embed = discord.Embed(
            description="You are not the owner of the bot!", color=RED_COLOR
        )
        await context.send(embed=embed)

        if context.guild:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) \
                    tried to execute an owner only command in the guild {context.guild.name} \
                        (ID: {context.guild.id}), but the user is not an owner of the bot."
            )

        else:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) \
                    tried to execute an owner only command in the bot's DMs, \
                        but the user is not an owner of the bot."
            )

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description="You are missing the permission(s) `"
            + ", ".join(error.missing_permissions)
            + "` to execute this command!",
            color=RED_COLOR,
        )
        await context.send(embed=embed)

    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            description="I am missing the permission(s) `"
            + ", ".join(error.missing_permissions)
            + "` to fully perform this command!",
            color=RED_COLOR,
        )
        await context.send(embed=embed)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error!",
            # We need to capitalize because the command
            # arguments have no capital letter in the code.
            description=str(error).capitalize(),
            color=RED_COLOR,
        )
        await context.send(embed=embed)
    else:
        raise error


async def load_cogs() -> None:
    """
    The code in this function is executed whenever the bot will start.
    """
    for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                bot.logger.info("Loaded extension '%s'", extension)
            except ImportError as error:
                exception = f"{type(error).__name__}: {error}"
                bot.logger.error(
                    "Failed to load extension %s\n%s", extension, exception)


asyncio.run(init_database())
asyncio.run(load_cogs())
bot.run(config["token"])
