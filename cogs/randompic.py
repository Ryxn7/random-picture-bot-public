import discord
from discord.ext import commands
import json
import aiohttp
from loguru import logger
import requests
import base64
import random


with open('data/database.json') as d:
    database = json.load(d)

with open('data/pictures.json') as f:
    pictures = json.load(f)


class randompic(commands.Cog):


    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        guildID = str(guild.id)
        pictures[guildID] = [0]
        pictures[guildID][0] = {}

        with open('data/pictures.json', 'w') as f:
            json.dump(pictures,f,indent=4)

        await self.pushdata()


    # Automatically push new data to Github
    async def pushdata(self):
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


    # Command to request images from Unsplash API
    @commands.command(aliases=['randpic', 'rp'])
    async def randompic(self, ctx, *word):


        word = list(word)

        name = " ".join(word).lower()
        query = "%20".join(word).lower()
        link = database["api_unsplash"].replace('[query]', query)
        data = requests.get(link).json()

        # Checks if the request can be found on Unsplash
        if data["total_pages"] == 0:
            await ctx.send(f"There are no pictures for {name} on Unsplash :/" \
                            "\nUse `b.add` to add pictures to the bots online database." \
                            "\n> Use `b.commands` to view how to use the command.")

        # Send a random picture of the request
        else:
            ok = random.randint(0, 9)

            photo = data["results"][ok]["urls"]["regular"]
            creator = data["results"][ok]["user"]["name"]
            create_date = data["results"][ok]["updated_at"][:-10]
            socials = data["results"][ok]["user"]["portfolio_url"]
            invite_link = database["invite_link"]


            embed = discord.Embed(title=f"**{name.title()}**", color=0x4ADEDE)

            embed.add_field(
                name = "Description",
                value = f'**Photo by:** {creator} on Unsplash' \
                        f'\n**Created on:** {create_date}' \
                        f'\n**Socials:** {socials}',
                inline = False
            )
            

            embed.set_footer(text=f"Invite the Random Picture Bot using this link! > {invite_link}")
            embed.set_image(url=photo)


            await ctx.send(embed=embed)
    

    # Command to add images to pictures.json if none are found on Unsplash API
    @commands.command(aliases=['a'])
    async def add(self, ctx, *np):

        np = list(np)
        pic = np[-1]
        new_np = np[:-1]
        desc = " ".join(new_np).lower()
        title = desc.capitalize()
        guildid = str(ctx.guild.id)

        unsplash_link = database["api_unsplash"].replace('[query]', desc)
        data = requests.get(unsplash_link).json()

        
        # Check if picture can be found on Unsplash
        if data["total_pages"] == 0:

            # Add to database if entry not found
            if desc not in pictures[guildid][0]:
                pictures[guildid][0][desc] = []
            pictures[guildid][0][desc].append(pic)
            await ctx.send(f"`{np[-1]}` was added to the Bot's database.")

        else:
            await ctx.send(f'{title} can be found on Unsplash!' \
                           f"> Use `b.rp` to search for {title}!")

        with open('data/pictures.json', 'w') as f:
            json.dump(pictures,f,indent=4)

        await self.pushdata()


    # Automatically push new data to Github
    async def pushdata(self):
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


    # Command to remove an image from the Bot's database
    @commands.command(aliases=['r'])
    async def remove(self, ctx, *rp):

        rp = list(rp)

        if len(rp) == 1:
            return await ctx.send("Please add the link of the image you would like to remove")
        
        else:
            pic = rp[-1]
            del_p = rp[:-1]
            desc = " ".join(del_p).lower()
            title = desc.capitalize()
            guildid = str(ctx.guild.id)

   
        if desc in pictures[guildid][0]:
            pictures[guildid][0][desc].remove(pic)
            await ctx.send(f"`{rp[-1]}` was removed from the Bot's database.")
            if pictures[guildid][0][desc] == []:
                del pictures[guildid][0][desc]

        else:
            await ctx.send(f"{title} does not exist on the Bot's database." \
                           f"> Use `b.l` to view the list of pictures on the Bot's database.")


        with open('data/pictures.json', 'w') as f:
            json.dump(pictures,f,indent=4)
        
        print("pictures.json was updated.")

        await self.pushdata()


    # Automatically push new data to Github
    async def pushdata(self):
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
    

    # Command that shows the list of added pictures
    @commands.command(aliases=["l"])
    async def list(self, ctx):
        
        guildId = str(ctx.guild.id)
        embed = discord.Embed(title="List of pictures on RPB's API", color=0x3acadf)

        pic_list = sorted(pictures[guildId][0])
        
        if len(pic_list) == 0:
            await ctx.send("There are currently no pictures stored on the Bot's database. Try adding pictures by using `b.add`!")

        list_of_pictures = ""
        for picture in pic_list:
            list_of_pictures += picture + " \n"
        
        embed.add_field(
            name = "Topics",
            value = list_of_pictures,
            inline = False
        )

        embed.set_footer(text="Use b.picture to access these pictures!")

        await ctx.send(embed=embed)


    # Command to retrieve and send the requested picture from the Bot's database
    @commands.command(aliases=["p"])
    async def picture(self, ctx, *word):

        word = list(word)

        name = " ".join(word).lower()
        guildId = str(ctx.guild.id)

        if name == "":
            return await ctx.send("> Use `b.list` to get the list of pictures that are available on RPB's database" \
                                  "\n> Use `b.add` to add your own pictures to RPB's database")
        # Return the requested image from pictures.json
        if name in pictures[guildId][0]:

            photo = pictures[guildId][0][name][random.randint(0, len(pictures[guildId][0][name]) - 1)]
    
            embed = discord.Embed(title=f"**{name.title()}**", color=0x5e59eb)

            embed.set_image(url=photo)
            embed.set_footer(text=f"> {photo}")

            await ctx.send(embed=embed)
        
        else:
            await ctx.send(f"{name} cannot be found on RPB's database" \
                            "\n> Use `b.list` to view the list of pictures that are available on RPB's database" \
                            "\n> Use `b.add` to add your own picture to RPB's database")


def setup(client):
    client.add_cog(randompic(client))
