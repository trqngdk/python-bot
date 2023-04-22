import platform
import random
from datetime import datetime
from typing import Final
from dataclasses import dataclass
from requests_cache import CachedSession
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

import discord
from helpers import checks

GREEN_COLOR = 0x72b01d  # Used to be 0x9C84EF
RED_COLOR = 0xb01d1f  # Used to be 0xE02B2B
BLACK_COLOR = 0x000000


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help", description="List all commands the bot has loaded."
    )
    @checks.not_blacklisted()
    async def help(self, context: Context) -> None:
        prefix = self.bot.config["prefix"]
        embed = discord.Embed(
            title="Help", description="List of available commands:", color=GREEN_COLOR
        )

        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            list_commands = cog.get_commands()
            data = []

            for command in list_commands:
                description = command.description.partition("\n")[0]
                data.append(f"{prefix}{command.name} - {description}")
            help_text = "\n".join(data)
            embed.add_field(
                name=i.capitalize(), value=f"```{help_text}```", inline=False
            )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="userinfo",
        description="Get some useful (or not) information about the userinfo.",
    )
    @checks.not_blacklisted()
    async def userinfo(self, ctx, *, user: discord.Member = None) -> None:
        """
        Get some useful (or not) information about the user.

        :param context: The hybrid command context.
        :param user: The user's info that going to be displayed.
        """

        if user is None:
            user = ctx.author
        date_format = "%a, %d %b %Y %I:%M %p"
        delta = datetime.utcnow() - user.created_at.replace(tzinfo=None)
        delta = str(delta).partition(',')[0]
        hypesquad_class = str(user.public_flags.all()).replace(
            '[<UserFlags.', '').replace('>]', '').replace('_', ' ').replace(':', '').title()

        embed = discord.Embed(
            title=user, color=BLACK_COLOR)
        embed.set_thumbnail(url=user.display_avatar)
        embed.add_field(name="Badges", value=hypesquad_class)
        embed.add_field(
            name="Origin", value=f"{user.created_at.strftime(date_format)} ({delta})", inline=False)
        embed.add_field(
            name="Joined", value=user.joined_at.strftime(date_format), inline=False)

        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
            embed.add_field(name="\n", value=role_string, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="botinfo",
        description="Get some useful (or not) information about the bot.",
    )
    @checks.not_blacklisted()
    async def botinfo(self, context: Context) -> None:
        """
        Get some useful (or not) information about the bot.

        :param context: The hybrid command context.
        """

        embed = discord.Embed(
            description="A normal python discord bot.",
            color=BLACK_COLOR
        )

        embed.set_author(name="Bot Information")
        embed.add_field(name="Owner:", value="trqngdk", inline=True)
        embed.add_field(
            name="Python Version:", value=f"{platform.python_version()}", inline=True
        )

        embed.add_field(
            name="Prefix:",
            value=f"/ (Slash Commands) or {self.bot.config['prefix']} for normal commands",
            inline=False,
        )

        embed.set_footer(text=f"Requested by {context.author}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="serverinfo",
        description="Get some useful (or not) information about the server.",
    )
    @checks.not_blacklisted()
    async def serverinfo(self, ctx) -> None:
        """
        Get some useful (or not) information about the server.

        :param ctx: The hybrid command context.
        """

        count = 0
        for member in ctx.guild.members:
            if member.status != discord.Status.offline:
                count += 1
        percentage = round(float(count / ctx.guild.member_count * 100), 2)

        embed = discord.Embed(
            title="trqngdk's Shelter",
            description="This server is owned by trqngdk", color=BLACK_COLOR)

        if ctx.guild.icon is not None:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embed.add_field(name="Created",
                        value=ctx.guild.created_at.strftime("%a, %d %b %Y"), inline=False)
        embed.add_field(name="Members",
                        value=f"{count} online out of {ctx.guild.member_count}\
                             ({percentage}%)", inline=False)

        embed.add_field(name="Booster",
                        value=ctx.guild.premium_subscription_count, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive.",
    )
    @checks.not_blacklisted()
    async def ping(self, context: Context) -> None:
        """
        Check if the bot is alive.

        :param context: The hybrid command context.
        """

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is `{round(self.bot.latency * 1000)}ms.`",
            color=GREEN_COLOR,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="invite",
        description="Get the invite link of the bot to be able to invite it.",
    )
    @checks.not_blacklisted()
    async def invite(self, context: Context) -> None:
        """
        Get the invite link of the bot to be able to invite it.

        :param context: The hybrid command context.
        """

        embed = discord.Embed(
            description=f"Invite me by clicking [here] \
                (https://discordapp.com/oauth2/authorize?&client_id={self.bot.config['application_id']}&scope=bot+applications.commands&permissions={self.bot.config['permissions']}).",
            color=0xD75BF4,
        )

        try:
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")

        except discord.Forbidden:
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="server",
        description="Get the invite link of the discord server of the bot for some support.",
    )
    @checks.not_blacklisted()
    async def server(self, context: Context) -> None:
        """
        Get the invite link of the discord server of the bot for some support.

        :param context: The hybrid command context.
        """

        embed = discord.Embed(
            description="Join the support server for the bot by clicking \
                [here](https://discord.gg/123456789).",
            color=0xD75BF4,
        )

        try:
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")

        except discord.Forbidden:
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="8ball",
        description="Ask any question to the bot.",
    )
    @checks.not_blacklisted()
    @app_commands.describe(question="The question you want to ask.")
    async def eight_ball(self, context: Context, *, question: str) -> None:
        """
        Ask any question to the bot.

        :param context: The hybrid command context.
        :param question: The question that should be asked by the user.
        """

        answers = [
            "It is certain.",
            "It is decidedly so.",
            "You may rely on it.",
            "Without a doubt.",
            "Yes - definitely.",
            "As I see, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again later.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]

        embed = discord.Embed(
            title="**My answer:**",
            description=f"{random.choice(answers)}",
            color=GREEN_COLOR,
        )

        embed.set_footer(text=f"The question was: {question}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="bitcoin",
        description="Get the current price of bitcoin.",
    )
    @checks.not_blacklisted()
    async def bitcoin(self, context: Context) -> None:
        """
        Get the current price of bitcoin.

        :param context: The hybrid command context.
        """

        url: Final = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'

        session = CachedSession(
            cache_name='cache/bitcoin_cache',
            expire_after=1
        )

        @dataclass
        class Price:
            time: str = None
            disclaimer: str = None
            bpi: str = None
            BTC: str = None

        response = session.get(url)

        try:
            json: dict = response.json()
            bpi = Price(**json)

            embed = discord.Embed(
                description=f"The current price is \
                    {bpi.bpi['USD']['rate']} dollar", color=GREEN_COLOR)
            await context.send(embed=embed)

        except ImportError as error:
            embed = discord.Embed(
                title="Error!",
                description=f"{response.status_code} - {error}",
                color=RED_COLOR,
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="covid",
        description="Get current covid status of Vietnam.",
    )
    @checks.not_blacklisted()
    async def covid(self, context: Context) -> None:
        """
        Get current covid status of Vietnam.

        :param context: The hybrid command context.
        """

        url: Final = 'https://api.apify.com/v2/key-value-stores/EaCBL1JNntjR3EakU/records/LATEST?disableRedirect=true'

        session = CachedSession(
            cache_name='cache/covid_cache',
            expire_after=1
        )

        @dataclass
        class Status:
            infected: str = None
            recovered: str = None
            treated: str = None
            died: str = None
            infectedToday: str = None
            recoveredToday: str = None
            treatedToday: str = None
            diedToday: str = None
            overview: str = None
            locations: str = None
            sourceUrl: str = None
            lastUpdatedAtApify: str = None
            readMe: str = None

        response = session.get(url)

        try:
            json: dict = response.json()
            status = Status(**json)

            embed = discord.Embed(
                title="Vietnam's Covid-19 Status", color=GREEN_COLOR)
            embed.add_field(name="Infected",
                            value=status.infected)
            embed.add_field(name="Recovered",
                            value=status.recovered)
            embed.add_field(name="Died", value=status.died)
            embed.add_field(name="Infected Today", value=status.infectedToday)
            embed.add_field(name="Recovered Today",
                            value=status.recoveredToday)
            embed.add_field(name="Died Today", value=status.diedToday)
            embed.timestamp = datetime.now()
            await context.send(embed=embed)

        except ImportError as error:
            embed = discord.Embed(
                title="Error!",
                description=f"{response.status_code} - {error}",
                color=RED_COLOR,
            )
            await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
