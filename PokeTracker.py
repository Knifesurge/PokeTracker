from discord.ext import commands
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

    load_poke()
    print(f'Tracked Pokes:', TRACKED_POKE, sep='\n')
    return

@bot.command(name="sd", hidden=True)
async def shutdown(ctx):
    if str(ctx.author.id) in OWNER_IDS:
        print("\n\n\n{}\n\t\tSHUTTING DOWN THE BOT!!!!!\n{}\n\n\n".format("="*70,"="*70))
        await bot.logout()
        exit()

@bot.command(name="rt", hidden=True)
async def restart(ctx):
    print(f'{ctx.author.name} ({ctx.author.id})')
    if str(ctx.author.id) in OWNER_IDS:
        cmd = 'py PokeTracker.py'
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
    for poke in TRACKED_POKE["pokes"]:
        for k, v in poke.items():
            print(k, v)
    return

def load_poke():
    global TRACKED_POKE
    # Load any Pokemon in the tracked-pokemon file
    # into the TRACKED_POKE dict
    with open("tracked-pokemon.json", "r") as f:
        data = json.load(f)
        print(data)
        TRACKED_POKE = data
        print(TRACKED_POKE)

@bot.command(name='ap', help='Add a Pokemon to track')
async def add_pokemon(ctx, *args):
    global TRACKED_POKE
    print('>> Command: add_pokemon')
    found = False
    count = 0
    poke = None

    name = args[0]
    num_hatched = args[1]
    finished = True if args[2] in ["Y", "y"] else False
    if len(args) > 3:
        trainer = args[3]
        if len(trainer) == 18:
            trainer = int(args[3])
    else:
        trainer = ctx.author.id

    print(name, num_hatched, finished, trainer, sep='\n')

    print("Finding pokemon...")
    while not found and count < len(TRACKED_POKE["pokes"]):
        poke = TRACKED_POKE["pokes"][count]
        print(f'Poke: {poke}')
        if poke["name"] == name and poke["trainer"] == trainer:
            found = True
        count += 1

    if found:
        print("FOUND!")
        count -= 1
        with open('tracked-pokemon.json', 'w') as f:
            old_num_hatched = poke["num_hatched"]
            x = {
                "name": name,
                "trainer": trainer,
                "num_hatched": int(num_hatched),
                "finished": finished,
                "start": poke["start"], # Copy old start time, this should never change
                "end": datetime.now().strftime("%c") if finished else None,
                "updated": datetime.now().strftime("%c")
            }
            # Overwrite previous data with new data
            TRACKED_POKE["pokes"][count] = x
            print(f'Old: {poke}\n\nNew: {x}')
            json.dump(TRACKED_POKE, f, indent=4)
            await ctx.channel.send(f'Updated your {name} entry! ({old_num_hatched}->{num_hatched})')
    else:   # Doesn't exist, create new
        print("NOT FOUND")
        with open('tracked-pokemon.json', 'w') as f:
            name = args[0]
            num_hatched = args[1]
            finished = True if args[2] in ["Y", "y"] else False
            x = {
                "name": name,
                "trainer": trainer,
                "num_hatched": int(num_hatched),
                "finished": finished,
                "start": datetime.now().strftime("%c"),
                "end": datetime.now().strftime("%c") if finished else None,
                "updated": None
            }
            # Overwrite previous data with new data
            TRACKED_POKE["pokes"].append(x)
            print(f'Wrote {x}\n to Tracked Pokes')
            json.dump(TRACKED_POKE, f, indent=4)
            await ctx.channel.send(f'Created your {name} entry!')



bot.run(TOKEN)
