import asyncio
import datetime
import re

from dotenv import load_dotenv
import os
import random

import discord
import discord.ext.commands as commands
from contsants import *
from pokeData import *

load_dotenv()

bot = commands.Bot(command_prefix='g!',
                   case_insensitive=True,
                   description="An all purpose discord bot",
                   activity=discord.Activity(name='Innerve Bot-a-thon', type=5),
                   status=discord.Status.idle,
                   intents=discord.Intents.all(),
                   strip_after_prefix=True
                   )


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')


CHANCE_OF_SPAWN = 15
spawnedMonData = {}
pokeData = {}


@bot.event
async def on_message(message: discord.Message):
    if not message.content.startswith(bot.command_prefix) and not message.author.bot:
        ctx = await bot.get_context(message)
        isSpawn = random.choices([True, False], weights=[CHANCE_OF_SPAWN * 100000, (100 - CHANCE_OF_SPAWN) * 100000], k=1)[0]
        if isSpawn:
            await spawn(message.channel)
        print(message.content)
    await bot.process_commands(message)


@bot.command(name='Ping', brief="Bot's Ping", help=f"Displays bot's latency\n\tUsage: **{bot.command_prefix} ping**")
async def _ping(ctx):
    await ctx.send(f"Pong! Bot latency is {bot.latency}")


@bot.command(name="Quit", brief="Quits Bot", help=f"Logs out the Bot. **(Owner)**\n\tUsage : **!2 quit**", hidden=True)
async def _quit(ctx):
    if ctx.author.id == 437491079869104138:
        await ctx.send(f"Disconnect sequence invoked by {ctx.author.display_name}...")
        await bot.logout()
    else:
        print(f"{ctx.author} tried to log out the bot.")


# Duel Command
async def duel_main(ctx, roundNum, author, opponent):
    if author.equipment == 'Potion':
        authorAttack = author.fight()
        opponentAttack = opponent.fight()
    else:
        opponentAttack = opponent.fight()
        authorAttack = author.fight()

    duelSim = discord.Embed(
        title=f"Duel between __{author.name}__ and __{opponent.name}__",
        colour=discord.Colour(0xFF6900),
        description=(f"{author.name} chose **{author.equipment}** and {opponent.name} chose **{opponent.equipment}**"
                     f"\n\n**Choose a new or the same weapon for the next round!**")
    )

    for i in (author, opponent):
        duelSim.add_field(name=f"__{i.name} ({i.health}/100)__", value=i.healthBar())

    duelSim.add_field(name=f"**__Round {roundNum}__**", inline=False, value=f"{authorAttack}\n\n\n{opponentAttack}")

    duelSim.set_author(name=author.name, icon_url=author.user.avatar_url)
    await author.message.edit(content=None, embed=duelSim)
    await author.next_round(roundNum, ctx)


class Dueler:
    def __init__(self, member: discord.Member, equipment: str, maxPotions: int = 3, opponent=None, mainMessage: discord.Message = None):
        self.user = member
        self.maxHP = 100
        self.health = self.maxHP
        self.equipment = equipment
        self.potionsLeft = maxPotions
        self.opponent = opponent
        self.name = member.display_name
        self.message = mainMessage

    def equipmentChange(self, weapon):
        self.equipment = weapon

    async def chooseEquipment(self, ctx, roundNum):
        booleans = [False, False]
        reactionsToRemove = []

        def check(r: discord.Reaction, u):
            if u.id != bot.user.id:
                reactionsToRemove.append((str(r.emoji), u))
            b = str(r.emoji)
            if u == self.user:
                if b in equipments.keys():
                    self.equipmentChange(equipments[b]['name'])
                    booleans[0] = True

            elif u == self.opponent.user:
                if b in equipments.keys():
                    self.opponent.equipmentChange(equipments[b]['name'])
                    booleans[1] = True
            return booleans[0] and booleans[1]

        try:
            await bot.wait_for(event='reaction_add', timeout=15.0, check=check)
            for i, j in reactionsToRemove:
                await self.message.remove_reaction(i, j)
        except asyncio.TimeoutError:
            await ctx.send('Timeout. You took too long!')
        else:
            await duel_main(ctx, roundNum, self, self.opponent)

    def healthBar(self) -> str:
        return "`" + "\u0020".join((["♥"] * (self.health // 10)) + (["♡"] * ((self.maxHP - self.health) // 10))) + "`"

    def attack(self, min_dmg, max_dmg, attack_chance) -> int:
        isHit = random.choices([True, False], weights=[attack_chance * 100000, (100 - attack_chance) * 100000], k=1)[0]
        if isHit:
            damageDealt = min([random.randint(min_dmg, max_dmg), self.opponent.health])
            self.opponent.health -= damageDealt
            return damageDealt
        return 0

    def fight(self) -> str:
        match self.equipment:
            case "Potion":
                if self.potionsLeft == 0:
                    return f"**{self.name}** tried to use a potion, but did not have any..."
                self.potionsLeft -= 1
                recoveredHealth = min(random.randint(20, 30), self.maxHP - self.health)
                self.health += recoveredHealth
                return f"**{self.name}** used a potion to heal **{recoveredHealth}** dmg (REMAINING POTIONS = {self.potionsLeft})"

            case "Knife":
                damageDealt = self.attack(min_dmg=10, max_dmg=20, attack_chance=90)
                if damageDealt:
                    return f"**{self.name}** stabbed **{self.opponent.name}** for __**{damageDealt}**__ Damage!"
            case 'Bow and Arrow':
                damageDealt = self.attack(min_dmg=40, max_dmg=50, attack_chance=60)
                if damageDealt:
                    return f"**{self.name}** took aim and shot the arrow at **{self.opponent.name}** for __**{damageDealt}**__ Damage!"
            case 'Gun':
                damageDealt = self.attack(min_dmg=90, max_dmg=100, attack_chance=20)
                if damageDealt:
                    return f"**{self.name}** managed to control the recoil and shot **{self.opponent.name}** for a WHOPPING __**{damageDealt}**__ Damage!!"

        return f"**{self.name}** missed **{self.opponent.name}** While using **{self.equipment}**"

    async def next_round(self, roundNum, ctx):
        if self.health == 0:
            if self.opponent.health == 0:
                await ctx.send(content=f"Both **{self.name}** AND **{self.opponent.name}** fainted, it's a TIE")
            else:
                await ctx.send(content=f"*{self.name}* fainted, hence, **{self.opponent.name} WINS**")
        elif self.opponent.health == 0:
            await ctx.send(content=f"*{self.opponent.name}* fainted, hence, **{self.name} WINS**")

        if self.opponent.health and self.health:
            await self.chooseEquipment(ctx=ctx, roundNum=roundNum + 1)


@bot.command()
async def duel(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Mention a user to duel with.")
        return

    weaponChoose = discord.Embed(
        title=f"Duel issued by __{ctx.author.display_name}__ against __{member.display_name}__",
        colour=discord.Colour(0xFF6900),
        description="Choose your equipment to Fight!"
    )

    weaponChoose.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)

    for w, desc in equipments.items():
        weaponChoose.add_field(name=w, value=desc["desc"])

    weaponChoose.add_field(
        name="\u3164", inline=False,
        value="Choose the First Equipment for either Side. You have 15 seconds."
    )

    chooseMsg = await ctx.send(embed=weaponChoose)

    equippedTool = {}
    booleans = [False, False]
    reactionsToRemove = []

    for weaponEmoji in equipments.keys():
        await chooseMsg.add_reaction(weaponEmoji)

    def check(r: discord.Reaction, u):
        if u.id != bot.user.id:
            reactionsToRemove.append((str(r.emoji), u))
        b = str(r.emoji)
        if u == ctx.author:
            if b in equipments.keys():
                equippedTool[ctx.author] = equipments[b]['name']
                booleans[0] = True

        elif u == member:
            if b in equipments.keys():
                equippedTool[member] = equipments[b]['name']
                booleans[1] = True
        return booleans[0] and booleans[1]

    try:
        await bot.wait_for(event='reaction_add', timeout=15.0, check=check)
        for i, j in reactionsToRemove:
            await chooseMsg.remove_reaction(i, j)
    except asyncio.TimeoutError:
        await ctx.send('Timeout. You took too long!')
    else:
        player1 = Dueler(ctx.author, equipment=equippedTool[ctx.author], mainMessage=chooseMsg)
        player2 = Dueler(member, opponent=player1, equipment=equippedTool[member], mainMessage=chooseMsg)
        player1.opponent = player2

        await duel_main(ctx, roundNum=1, author=player1, opponent=player2)


# Duel Command Ends


# PokeCord Stuff
@bot.command(aliases=['start'])
async def starter(ctx, choice: str = None):
    choice = choice.strip() if choice is not None else choice
    if ctx.author in pokeData.keys():
        ctx.send("You have already gotten a starter.")
        return
    if choice is None or choice.lower() not in starterNames:
        start = discord.Embed(
            title="Choose a Starter PokéMon for your Journey" if choice is None else "INVALID CHOICE! Choose starter from this list only.",
            description=f"To choose a starter, type **{bot.command_prefix}starter <starter pokemon name>**!",
            colour=discord.Colour(0xff6900)
        )
        start.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        start.set_image(url="https://static.wikia.nocookie.net/pokeverse/images/4/46/Pokemon_starters_.png/revision/latest?cb=20180424013225")
        for region, types in starters.items():
            start.add_field(
                name=region, inline=True,
                value=f"🔥 - {types['fire']}\n💧 - {types['water']}\t\n🍃 - {types['grass']}"
            )
        start.set_thumbnail(
            url='https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/International_Pokémon_logo.svg/640px-International_Pokémon_logo.svg.png'
        )
        await ctx.send(embed=start)
    else:
        start = discord.Embed(
            title=f"You chose {choice.capitalize()} as your starter!",
            description=f"NOTE: Starter cannot be changed later. To confirm, please react with ✅, else ❎",
            colour=discord.Colour(0xff6900)
        )
        start.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        pokemon = generate(name=choice.lower(), minLvl=5, maxLvl=5)
        start.set_image(url=pokemon.image)
        message = await ctx.send(embed=start)
        await message.add_reaction(emoji="✅")
        await message.add_reaction(emoji="❎")

        def check(reac, user):
            if user == ctx.author and reac.emoji in "✅❎":
                return True

        try:
            r, u = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            await message.remove_reaction(r.emoji, u)
        except asyncio.TimeoutError:
            ctx.send("TIMEOUT! Please choose again later.")
        else:
            if r.emoji == "❎":
                await ctx.send(f"**{choice.capitalize()}** was not chosen as starter pokemon.")
            if r.emoji == "✅":
                pokeData[ctx.author] = [pokemon]
                starterMon = discord.Embed(
                    title="Starter chosen!",
                    description=f"{choice.capitalize()} was chosen to be your starter pokemon!",
                    colour=discord.Colour(0xff6900)
                )
                starterMon.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                starterMon.set_image(url=pokemon.image)

                starterMon.add_field(
                    name=f"IV Stats", inline=True,
                    value='\n'.join(f"{k} : {v}" for k, v in pokemon.stats.items())
                )
                await ctx.send(embed=starterMon)


@bot.command(aliases=['dex', 'bag', 'show'])
async def pokemons(ctx):
    if ctx.author not in pokeData.keys():
        await ctx.send("You have not picked a starter yet.")
        await starter(ctx)
        return
    desc = ""
    for i, mon in enumerate(pokeData[ctx.author], start=1):
        desc += f"{i: >3})_   _**{mon.name.capitalize()}** - Level {mon.level}\n"
    mons = discord.Embed(title="List of pokémons you have caught", colour=discord.Colour(0xff6900),
                         description=f"Here are pokemons you have caught yet.\n{desc}")
    await ctx.send(embed=mons)


def generate(pokeNum=None, name=None, minLvl=1, maxLvl=100):
    if name is not None:
        data = fetch_data_by_name(name=name)
    elif pokeNum is not None:
        data = fetch_data(pokeNumber=pokeNum)
    else:
        pokemonNumber = random.randint(1, 809)
        data = fetch_data(pokeNumber=pokemonNumber)

    stats = {
        "HP     ": random.randint(0, 31),
        "ATK    ": random.randint(0, 31),
        "DEF    ": random.randint(0, 31),
        "SPEED  ": random.randint(0, 31),
        "SP. ATK": random.randint(0, 31),
        "SP. DEF": random.randint(0, 31)
    }

    level = random.randint(minLvl, maxLvl)

    pokemon = Pokemon(pokeNum=data['id'], name=data['name'], level=level, image=data['image'], stats=stats, types=data['types'])
    return pokemon


@bot.command()
async def info(ctx, flag: str):
    if ctx.author not in pokeData.keys():
        await ctx.send("You have not picked a starter yet.")
        await starter(ctx)
        return
    mon = pokeData[ctx.author][-1]
    if flag.lower() == 'latest':
        pass
    else:
        try:
            pokemonNumber = int(flag) - 1
            mon = pokeData[ctx.author][pokemonNumber]
        except (IndexError, BaseException):
            await ctx.send("INVALID NUMBER")
            return
    caughtEmbed = discord.Embed(
        title=f"Level {mon.level} {mon.name.capitalize()}",
        colour=discord.Colour(0xff6900),
        description=f"Type : {mon.typeString()}"
    )
    caughtEmbed.set_image(url=mon.image)
    caughtEmbed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    caughtEmbed.add_field(
        name=f"IV Stats", inline=True,
        value='\n'.join(f"{k} : {v}" for k, v in mon.stats.items())
    )
    await ctx.send(embed=caughtEmbed)


# @bot.command(enabled = False)
async def spawn(channel):
    mon = generate()
    spawnEmbed = discord.Embed(
        title="Pokémon Spawn!",
        description=f"Type **{bot.command_prefix}catch <pokemon name>** to catch!",
        colour=discord.Colour(0xff6900)
    )
    spawnEmbed.set_author(name=bot.user.display_name, icon_url=bot.user.avatar_url)
    spawnEmbed.set_image(url=mon.image)

    await channel.send(embed=spawnEmbed)
    spawnedMonData["channel"] = channel
    spawnedMonData["mon"] = mon


@bot.command()
async def catch(ctx, pokemonName):
    if ctx.author not in pokeData.keys():
        await ctx.send("You have not picked a starter yet.")
        await starter(ctx)
        return
    channel = spawnedMonData["channel"]
    mon = spawnedMonData["mon"]
    if channel is None or ctx.channel != channel:
        await ctx.send("No pokemon is available to catch")
        return
    if pokemonName.lower() == mon.name.lower():
        pokeData[ctx.author].append(mon)
        await channel.send(f"Congratulations **{ctx.author}**! You caught a level {mon.level} {mon.name.capitalize()}!!\n"
                           f"Type **{bot.command_prefix}info latest** to view!")
        spawnedMonData["channel"] = None
        spawnedMonData["mon"] = None


bot.run(os.getenv('TOKEN'))
