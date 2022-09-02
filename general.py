import discord
from discord.ext import commands, tasks
from loguru import logger
import json
import base64
import aiohttp


with open('data/database.json') as d:
    database = json.load(d)


class General(commands.Cog):
        
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        invite_link = database["invite_link"]
        activity = discord.Game(name = f"b.help | {invite_link}")
        await self.client.change_presence(status=discord.Status.online, activity=activity)
        logger.info("Random Picture Bot is ready.")


    @commands.command()
    async def hi(self, ctx):
        if ctx.author.id == 367469641150365702:
            await ctx.send('Heya!')
    

    # Returns the User's ping
    @commands.command()
    async def ping(self, ctx):
        ping = int(round(self.client.latency * 1000))
        await ctx.send(f"Pong! Your ping is {ping}ms")


    # Returns information on how to use the bot        
    @commands.command(aliases=['h'])
    async def help(self, ctx):

        embed = discord.Embed(
            title="Random Picture Bot | Help",
            color=0x7FFFD4
            )

        embed.add_field(
            name = "About this bot:",
            value = "Random Pic Bot is the all-in-one bot for requesting any picture you desire! " \
                    "Simply enter anything you would like a picture of and Random Pic Bot will reply with a picture of your request. Enjoy!",
            inline = False
        )

        embed.add_field(
            name = "Commands List",
            value = "`b.commands` > Returns the list of Random Pictures Bot's commands!" \
                    "\nAliases: `b.command`, `b.c`",
            inline = False
        )

        embed.add_field(
            name = "Bot Invite Link",
            value = "`b.invite` > Returns the bot's invite link" \
                    "\nAliases: `b.i`",
            inline = False
        )
        
        image = "https://img.freepik.com/premium-vector/sakura-flowers-background-cherry-blossom-isolated-white-background_38668-274.jpg?w=996"
        embed.set_thumbnail(url=image)
        embed.set_footer(text="By Ryxn <3")

        await ctx.send(embed=embed)
    

    # Returns the invite link for the Bot
    @commands.command(aliases=['i'])
    async def invite(self, ctx):

        invite_link = database["invite_link"]
        message = "Invite Random Picture Bot to your own server using this link!" \
                  f"\n> {invite_link}"
                  
        await ctx.send(message)


    # Returns a list of commands that offered by the Bot
    @commands.command(name='commands', aliases=['command', 'c'])
    async def _commands(self, ctx):

        embed = discord.Embed(
            title="Commands List",
            color=0x40E0D0
            )

        embed.add_field(
            name = "***b.help***",
            value = "> Returns the help prompt." \
                    "\n> `(Aliases: b.h)`",
            inline = False
        )

        embed.add_field(
            name = "***b.randompic (pic_req)***",
            value = "> Returns the a random picture of your request!" \
                    "\n> `(Aliases: b.randpic, b.rp)`" \
                    "\n> `Ex: b.randompic dog`",
            inline = False
        )

        embed.add_field(
            name = "***b.add (pic_name) (link)***",
            value = "> Use this command to add pictures to the bot's online database!" \
                    "\n> `(Aliases: b.a)`" \
                    "\n> `Ex: b.add vega65 (image_link)`",
            inline = False
        )

        embed.add_field(
            name = "***b.remove (pic_name) (link)***",
            value = "> Use this command to remove a picture from the bot's online database!" \
                    "\n> `(Aliases:  b.r)`" \
                    "\n> `Ex: b.remove vega65 (image_link)`",
            inline = False
        )

        embed.add_field(
            name = "***b.list***",
            value = "> Returns the list of pictures on the bot's online database!" \
                    "\n> `(Aliases: b.l)`",
            inline = False
        )

        embed.add_field(
            name = "***b.picture (pic_name)***",
            value = "> Returns the requested picture from the bot's online database!" \
                    "\n> `(Aliases: b.p)`" \
                    "\n> `Ex: b.picture vega65`",
            inline = False
        )

        embed.add_field(
            name = "***b.invite***",
            value = "> Returns the invite link for Random Picture Bot!" \
                    "\n> `(Aliases: b.i)`",
            inline = False
        )

        embed.add_field(
            name = "***b.ping***",
            value = "> Returns your ping!",
            inline = False
        )

        await ctx.send(embed=embed)


    # Command to push changes made to pictures.json to Github
    @commands.command()
    async def gitPush(self, ctx):
        if ctx.author.id == 367469641150365702:
            filenames = ["data/pictures.json"]
            for filename in filenames:
                try:
                    token = database["github_oath"]
                    repo = "Ryxn7/Random-Pic-Bot"
                    branch = "main"
                    url = "https://api.github.com/repos/" + repo + "/contents/" + filename

                    base64content = base64.b64encode(open(filename, "rb").read())

                    async with aiohttp.ClientSession() as session:
                        async with session.get(url + '?ref=' + branch, headers={"Authorization": "token " + token}) as data:
                            data = await data.json()
                    sha = data['sha']

                    if base64content.decode('utf-8') + "\n" != data['content']:
                        message = json.dumps(
                            {"message": "Automatic data update.",
                            "branch": branch,
                            "content": base64content.decode("utf-8"),
                            "sha": sha}
                        )

                        async with aiohttp.ClientSession() as session:
                            async with session.put(url, data=message, headers={"Content-Type": "application/json",
                                                                               "Authorization": "token " + token}) as resp:
                                print(resp)   
                    else:
                        print("Nothing to update.")
                except Exception as e:
                    logger.exception(e)
            await ctx.send("Pushed latest data to GitHub.")


def setup(client):
    client.add_cog(General(client))