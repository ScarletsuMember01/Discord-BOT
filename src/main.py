import discord
from discord.ext import commands, tasks
import random
from urllib.request import urlopen
import json
from collections import defaultdict

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True, # Commands aren't case-sensitive
    intents = intents # Set up basic permissions
)
# Store user message counts and timestamps
user_message_counts = defaultdict(int)
user_message_timestamps = {}
user_cooldowns = {}
flood_monitoring_active = False
bot.author_id = 272746326947790849  # Change to your discord id

# bot.load_extension("cogs.moderation")
# bot.load_extension("cogs.commands")

@bot.event
async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier

@bot.command()
async def pong(ctx):
    await ctx.send('pong')

@bot.command(name="name")
async def name(ctx):
    user = ctx.message.author
    await ctx.send(f'Your name is {user.display_name}')
    
@bot.command(name="d6")
async def d6(ctx):
    result = random.randint(1, 6)
    await ctx.send(f'You rolled a d6 and got {result}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == "Salut tout le monde":
        await message.channel.send(f"Salut tout seul {message.author.mention}")

    await bot.process_commands(message)

@bot.event
async def on_message(message):
    global flood_monitoring_active
    if flood_monitoring_active and message.author != bot.user:
        author_id = message.author.id
        if author_id in user_message_counts:
            user_message_counts[author_id] += 1
        else:
            user_message_counts[author_id] = 1
        
        if user_message_counts[author_id] > 10:
            await message.channel.send(f"{message.author.mention}, Lache ton clavier et touche de l'herbe la !")

    await bot.process_commands(message)
    
@tasks.loop(minutes=1)
async def clear_message_counts():
    user_message_counts.clear()

@bot.command(name="admin")
async def give_admin_role(ctx, member: discord.Member):
    guild = ctx.guild

    # Check if the Admin role exists, and create it if it doesn't
    admin_role = discord.utils.get(guild.roles, name="Admin")
    if admin_role is None:
        admin_role = await guild.create_role(name="Admin")

        # Define permissions for the Admin role
        permissions = discord.Permissions()
        permissions.update(
            manage_channels=True,
            kick_members=True,
            ban_members=True
        )

        await admin_role.edit(permissions=permissions)

    # Assign the Admin role to the specified member
    await member.add_roles(admin_role)
    await ctx.send(f"{member.mention} has been given the Admin role.")

@bot.command(name="ban")
async def ban_member(ctx, member: discord.Member, ban_reason="Flop trop"):
    if (member.id == bot.author_id):
        await ctx.send("You can't ban the bot owner!")
        return
    await member.ban(reason=ban_reason)
    await ctx.send(f"{member.mention} has been banned. Reason: {ban_reason}")

@bot.command(name="flood")
async def flood(ctx):
    global flood_monitoring_active
    if flood_monitoring_active == False:
        flood_monitoring_active = True
        await ctx.send("Message monitoring on")
        clear_message_counts.start()
    else:
        flood_monitoring_active = False
        await ctx.send("Message monitoring off")
        user_message_counts.clear()

@bot.command(name="xkcd")
async def get_random_xkcd(ctx):
    random_comic_num = random.randint(1, 2500)
    xkcd_url = f"https://xkcd.com/{random_comic_num}/info.0.json"
    try:
        response = urlopen(xkcd_url)
        data = response.read().decode("utf-8")

        img_url = json.loads(data)["img"]

        await ctx.send(f"{img_url}")
    except Exception as e:
        await ctx.send("Error fetching")

@bot.command(name="poll")
async def create_poll(ctx, question):
    # Send an @here mention followed by the poll question
    poll_message = await ctx.send(f"@here {question}")

    # Add emoji reactions to the poll message
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎") 

token = "MTE2Njc4NTk2Mjc0Mzk2MzcxOQ.GPP4AZ.oL0FqlkNyZbcFbRQAI0ry2S0zpfw7BWbUI5iWY"
bot.run(token)  # Starts the bot