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
        activity = discord.Game(name = f"/help | {invite_link}")
        await self.client.change_presence(status=discord.Status.online, activity=activity)
        logger.info("Random Picture Bot is ready.")


    @discord.slash_command(name='hi')
    async def hi(self, ctx):
        if ctx.author.id == 367469641150365702:
            await ctx.respond('Heya!')
    

    # Returns the User's ping
    @discord.slash_command(name='ping')
    async def ping(self, ctx):
        ping = int(round(self.client.latency * 1000))
        await ctx.respond(f"Pong! Your ping is {ping}ms")


    # Returns information on how to use the bot        
    @discord.slash_command(name='help', description='Help Prompt for the Bot')
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
            value = "`/commands` > Returns the list of Random Pictures Bot's commands!",
            inline = False
        )

        embed.add_field(
            name = "Bot Invite Link",
            value = "`/invite` > Returns the bot's invite link",
            inline = False
        )
        
        image = "https://img.freepik.com/premium-vector/sakura-flowers-background-cherry-blossom-isolated-white-background_38668-274.jpg?w=996"
        embed.set_thumbnail(url=image)
        embed.set_footer(text="By Ryxn <3")

        await ctx.respond(embed=embed)
    

    # Returns the invite link for the Bot
    @discord.slash_command(name='invite', description="Random Picture Bot's Invite link")
    async def invite(self, ctx):

        invite_link = database["invite_link"]
        message = "Invite Random Picture Bot to your own server using this link!" \
                  f"\n> {invite_link}"
                  
        await ctx.respond(message)


    # Returns a list of commands that offered by the Bot
    @discord.slash_command(name='commands', description='Commands List')
    async def _commands(self, ctx):

        embed = discord.Embed(
            title="Commands List",
            color=0x40E0D0
            )

        embed.add_field(
            name = "***/help***",
            value = "> Returns the Bot's help prompt.",
            inline = False
        )

        embed.add_field(
            name = "***/randompic (pic_req)***",
            value = "> Returns a random picture of your request!"
                    "\n> `Ex: /randompic dog`",
            inline = False
        )

        embed.add_field(
            name = "***/add (pic_name) (link)***",
            value = "> Use this command to add pictures to the bot's online database!"
                    "\n> `Ex: /add vega65 (image_link)`",
            inline = False
        )

        embed.add_field(
            name = "***/remove (pic_name) (link)***",
            value = "> Use this command to remove a picture from the bot's online database!"
                    "\n> `Ex: /remove vega65 (image_link)`",
            inline = False
        )

        embed.add_field(
            name = "***/list***",
            value = "> Returns the list of pictures on the bot's online database!",
            inline = False
        )

        embed.add_field(
            name = "***/picture (pic_name)***",
            value = "> Returns the requested picture from the bot's online database!"
                    "\n> `Ex: /picture vega65`",
            inline = False
        )

        embed.add_field(
            name = "***/invite***",
            value = "> Returns the invite link for Random Picture Bot!",
            inline = False
        )

        embed.add_field(
            name = "***/ping***",
            value = "> Returns your ping!",
            inline = False
        )

        await ctx.respond(embed=embed)


    # Command to push changes made to pictures.json to Github
    @discord.slash_command(name='gitpush', description="Manually push new data to the Bot's online database")
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
            await ctx.respond("Pushed latest data to GitHub.")


def setup(client):
    client.add_cog(General(client))
