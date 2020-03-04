from discord.ext import commands
from discord.utils import get
from discord import Embed
import asyncio
import os
import subprocess
import json
from datetime import datetime
import time

TOKEN = os.getenv('POKETRACKER_TOKEN')

OWNER_IDS = [
    "205166483284819969",   # Knifesurge#1723
    "318644989556949003"    # Carlos94563#0697
]

TRACKED_POKE = {"pokes": []}
TRACKED_POKE_FN = "tracked-pokemon.json"
SHINY_POKE = {"shinies": []}
SHINY_POKE_FN = "shiny-pokemon.json"

bot = commands.Bot(command_prefix='!', description="""
PokeTracker is a Discord Bot written in Discord.py by Knifesurge#1723. Please contact me
if you have any problems with the bot. Have a great day!
""")

# REMINDER: You can't use on_message and the command() decorators at the same time,
# only the on_message event will fire and not the commands

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


    load_shiny_poke()
    load_tracked_poke()
    print(f'Tracked Pokes:', TRACKED_POKE, sep='\n')
    print(f'Shiny Pokes:', SHINY_POKE, sep='\n')
    return

def is_admin(id : int) -> bool:
    return str(id) in OWNER_IDS

async def get_username(ctx, user_id : int) -> str:
    return await ctx.message.server.get_member(user_id).display_name

@bot.command(name="sd", hidden=True)
async def shutdown(ctx):
    if is_admin(ctx.author.id):
        print("\n\n\n{}\n\t\tSHUTTING DOWN THE BOT!!!!!\n{}\n\n\n".format("="*70,"="*70))
        await bot.logout()
        exit()

@bot.command(name="rt", hidden=True)
async def restart(ctx):
    print(f'{ctx.author.name} ({ctx.author.id})')
    if is_admin(ctx.author.id):
        cmd = 'python PokeTracker.py'
        print("\n\n\n{}\n\t\tRESTARTING THE BOT!!!!!\n{}\n\n\n".format("="*60,"="*60))
        subprocess.run(cmd, shell=True)
        time.sleep(0.2)
        quit()

@bot.command()
async def test(ctx):
    counter = 0
    tmp = await ctx.channel.send('Calculating messages...')
    async for log in ctx.channel.history().filter(lambda m: m.author == ctx.author):
        counter += 1
    await tmp.edit(content='You have {} messages!'.format(counter))

@bot.command()
async def sleep(ctx):
    await asyncio.sleep(5)
    await ctx.channel.send('Done sleeping')

@bot.command(name='hw', help='Says "Hello, World!"')
async def helloworld(ctx):
    print('>> Command: helloworld')
    await ctx.send('Hello, World!')

""" =========== ACTUAL POKEMON RELATED COMMANDS =========== """

@bot.command(name='pp', help='Prints tracked Pokemon')
async def print_pokemon(ctx):
    global TRACKED_POKE
    global SHINY_POKE
    if is_admin(ctx.author.id):
        print("="*30,"Tracked Pokemon","="*30,sep='\n')
        for poke in TRACKED_POKE["pokes"]:
            for k, v in poke.items():
                print(k, v)
        print("="*30,"Tracked Pokemon","="*30,sep='\n')
        for poke in SHINY_POKE["shinies"]:
            for k, v in poke.items():
                print(k, v)
        print("="*30)
    return

def load_shiny_poke():
    global SHINY_POKE
    with open(SHINY_POKE_FN, 'r') as f:
        data = json.load(f)
        SHINY_POKE = data
    return

def load_tracked_poke():
    global TRACKED_POKE
    # Load any Pokemon in the tracked-pokemon file
    # into the TRACKED_POKE dict
    with open(TRACKED_POKE_FN, "r") as f:
        data = json.load(f)
        #print(data)    #DEBUG
        TRACKED_POKE = data
        #print(TRACKED_POKE)    # DEBUG
    return

@bot.command(name='as', help='Add a shiny Pokemon')
async def add_shiny(ctx, *args):
    global SHINY_POKE
    name = args[0]
    num = args[1]
    trainer = ctx.author.id
    date_obtained = []
    for i in range(len(args[2:])):
        date_obtained.append(args[i])
    " ".join(date_obtained)

    found = False
    index = 0
    poke = None
    while not found and index < len(SHINY_POKE):
        poke = SHINY_POKE["shinies"][index]
        if poke["name"] == name and poke["trainer"] == trainer:
            found = True
        index += 1
    
    if found:
        index -= 1
        old_num = poke["count"]
        # Update existing entry
        with open(SHINY_POKE_FN, "a+") as f:
            x = {
                "name": name,
                "trainer_id": trainer,
                "trainer": get_username(ctx, trainer),
                "count": num,
                "obtained": poke["obtained"],
                "updated": datetime.now().strftime("%c")
            }
            json.dump(x, f, indent=4)
            await ctx.channel.send(f'Updated your shiny count for {name}! ({old_num}->{num})')
    else:
        # Create new entry
        with open(SHINY_POKE_FN, "a+") as f:
            x = {
                "name": name,
                "trainer_id": trainer,
                "trainer": get_username(ctx, trainer),
                "count": num,
                "obtained": datetime.now().strftime("%c"),
                "updated": datetime.now().strftime("%c")
            }
            json.dump(x, f, indent=4)


@bot.command(name='display', help='Displays tracked Pokemon')
async def display_pokemon(ctx, *args):
    global TRACKED_POKE
    print(">> Command: display_pokemon")
    print(f'>> Args: {args}')
    
    # Process args, and display accordingly
    if len(args) == 0:

        embeded = Embed(title=ctx.author.name+"'s Tracked Pokemon!")

        for poke in TRACKED_POKE["pokes"]:
            if poke["trainer_id"] == ctx.author.id:
                for k, v in poke.items():
                    embeded.add_field(name=k+":", value=v, inline=False)
    elif len (args) == 1 and args[0] == "all" and is_admin(ctx.author.id):
        embeded = Embed(title="All Tracked Pokemon!")

        for poke in TRACKED_POKE["pokes"]:
            for k, v in poke.items():
                embeded.add_field(name=k+":", value=v, inline=False)
    elif len(args) == 1 and args[0] in ["shiny", "s"]:
        embeded = Embed(title=ctx.author.name+"'s Shiny Pokemon!")

        for poke in SHINY_POKE["shinies"]:
            if poke["trainer_id"] == ctx.author.id:
                for k, v in poke.items():
                    embeded.add_field(name=k+":", value=v, inline=False)
    elif len(args) == 2 and args[0] == "all" \
    and args[1] == "shiny" and is_admin(ctx.author.id):
        embeded = Embed(title="All Shiny Pokemon!")

        for poke in SHINY_POKE["shinies"]:
                for k, v in poke.items():
                    embeded.add_field(name=k+":", value=v, inline=False)
      
    await ctx.channel.send(embed=embeded)

@bot.command(name='rp', help='Remove a tracked Pokemon')
async def remove_pokemon(ctx, *args):
    global TRACKED_POKE
    print(">> Command: remove_pokemon")
    removed = False
    name = args[0]
    curr_poke = None
    index = 0

    while not removed and index < len(TRACKED_POKE["pokes"]):
        curr_poke = TRACKED_POKE["pokes"][index]
        if curr_poke["name"] == name and curr_poke["trainer_id"] == ctx.author.id:
            del TRACKED_POKE["pokes"][index]
            removed = True
        index += 1
    
    if removed:
        with open(TRACKED_POKE_FN, 'w') as f:
            json.dump(TRACKED_POKE, f, indent=4)
        await ctx.channel.send(f'Successfully removed the tracked Pokemon {name}!')
    else:
        await ctx.channel.send(f'Unable to find the tracked Pokemon {name}! If you \
            believe this to be in error, please contact Knifesurge#1723')

@bot.command(name='rs', help='Remove a tracked Pokemon')
async def remove_shiny_pokemon(ctx, *args):
    global SHINY_POKE
    print(">> Command: remove_shiny_pokemon")
    removed = False
    name = args[0]
    curr_poke = None
    index = 0

    while not removed and index < len(SHINY_POKE["shinies"]):
        curr_poke = SHINY_POKE["shinies"][index]
        if curr_poke["name"] == name and curr_poke["trainer_id"] == ctx.author.id:
            del SHINY_POKE["shinies"][index]
            removed = True
        index += 1
    
    if removed:
        with open(SHINY_POKE_FN, 'w') as f:
            json.dump(SHINY_POKE, f, indent=4)
        await ctx.channel.send(f'Successfully removed the shiny Pokemon {name}!')
    else:
        await ctx.channel.send(f'Unable to find the shiny Pokemon {name}! If you \
            believe this to be in error, please contact Knifesurge#1723')


@bot.command(name='ap', help='Add a Pokemon to track')
async def add_pokemon(ctx, *args):
    global TRACKED_POKE
    print('>> Command: add_pokemon')
    found = False
    count = 0
    poke = None
    repeats = 0

    name = args[0]
    num = args[1]
    finished = True if args[2] in ["Y", "y"] else False
    trainer = ctx.author.id
    repeats = args[3] if len(args) > 3 else ""

    while count < len(TRACKED_POKE["pokes"]):
        poke = TRACKED_POKE["pokes"][count]
        if poke["name"] == name and poke["trainer_id"] == trainer:
            found = True
        count += 1

    if found:
        count -= 1
        with open(TRACKED_POKE_FN, 'a+') as f:
            old_num = poke["num"]
            x = {
                "name": name + repeats,
                "trainer_id": trainer,
                "trainer": get_username(ctx, trainer),
                "num": int(num),
                "finished": finished,
                "start": poke["start"], # Copy old start time, this should never change
                "end": datetime.now().strftime("%c") if finished else None,
                "updated": datetime.now().strftime("%c")
            }
            # Overwrite previous data with new data
            TRACKED_POKE["pokes"][count] = x
            #print(f'Old: {poke}\n\nNew: {x}')  # DEBUG
            json.dump(TRACKED_POKE, f, indent=4)
            await ctx.channel.send(f'Updated your {name} entry! ({old_num}->{num})')
    else:   # Doesn't exist, create new
        #print("NOT FOUND") # DEBUG
        with open(TRACKED_POKE_FN, 'a+') as f:
            name = args[0]
            num = args[1]
            finished = True if args[2] in ["Y", "y"] else False
            x = {
                "name": name + repeats,
                "trainer_id": trainer,
                "trainer": get_username(ctx, trainer),
                "num": int(num),
                "finished": finished,
                "start": datetime.now().strftime("%c"),
                "end": datetime.now().strftime("%c") if finished else None,
                "updated": None
            }
            # Overwrite previous data with new data
            TRACKED_POKE["pokes"].append(x)
            #print(f'Wrote {x}\n to Tracked Pokes') # DEBUG
            json.dump(TRACKED_POKE, f, indent=4)
            await ctx.channel.send(f'Created your {name} entry!')
    return

if __name__ == '__main__':
    bot.run(TOKEN)
