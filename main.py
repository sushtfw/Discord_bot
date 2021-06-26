# Libraries
import platform
import selenium

import discord  # For discord
from discord.ext import commands  # For discord
import logging  # For logging
from pathlib import Path  # For paths
import json

from discord.ext.commands import MissingPermissions, has_permissions

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n cwd")

# Defining a few things
secret_file = json.load(open(cwd+'/token.json'))
bot = commands.Bot(command_prefix='-', case_insensitive=True)
bot.config_token = secret_file['TOKEN']
logging.basicConfig(level=logging.INFO)


bot.version = '0.0.1'


@bot.event
async def on_command_error(ctx, error):
    # Ignore these errors
    ignored = (commands.CommandNotFound, commands.UserInputError)
    if isinstance(error, ignored):
        return

    # Begin error handling
    if isinstance(error, commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)
        if int(h) == 0 and int(m) == 0:
            await ctx.send(f' You must wait {int(s)} seconds to use this command!')
        elif int(h) == 0 and int(m) != 0:
            await ctx.send(f' You must wait {int(m)} minutes and {int(s)} seconds to use this command!')
        else:
            await ctx.send(f' You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("Hey! You lack permission to use this command.")
    raise error


@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name} : {bot.user.id}\nMy current prefix is: -')
    await bot.change_presence(activity=discord.Game(name=f'Hi, my name is {bot.user.name}.\nThe current prefix is "-"'))
    # This changes the bots 'activity'


@bot.command(name='hi', aliases=['hello'])
async def _hi(ctx):
    await ctx.send(f'Hi {ctx.author.mention}!')
    # A simple command which says hi to the author.


@bot.command()
@commands.has_guild_permissions(ban_members=True)
async def stats(ctx):
    pythonversion = platform.python_version()
    dpyversion = discord.__version__
    servercount = len(bot.guilds)
    membercount = len(set(bot.get_all_members()))
    await ctx.send(f'I am in {servercount} guilds with a total of {membercount} members.'
                   f'\nThe bot is running on python {pythonversion} and discord.py on {dpyversion}')
    # Displays the statistics of the bot.


@bot.command(aliases=['disconnect', 'close', 'stop'])
@commands.has_guild_permissions(ban_members=True)
async def logout(ctx):
    await ctx.send(f"Hey {ctx.author.mention}, I am now logging out :wave:")
    await bot.logout()
    # To stop the bot.


@logout.error
async def logout_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Hey! You lack permission to use this command as you do not own the bot.")
    else:
        raise error
    # If people without perms stop the bot.


@bot.command()
async def echo(ctx, message=None):
    await ctx.message.delete()
    if message.author.has_permissions:
        await ctx.send(message)
    else:
        await ctx.send(f'You, {message.author.mention} are not eligible to do that here')
    # A simple command that repeats the users input back to them.


@bot.command()
@commands.has_guild_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    guild = member.guild
    if guild.system_channel is not None:
        to_send = '{0.mention} has been kicked from {1.name}'.format(member, guild)
        await guild.system_channel.send(to_send)
    # A command to kick members from the server.


@bot.command()
@commands.has_guild_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    guild = member.guild
    if guild.system_channel is not None:
        to_send = '{0.mention} has been banned from {1.name}'.format(member, guild)
        await guild.system_channel.send(to_send)
    # A command to ban members.


@bot.command()
@commands.has_guild_permissions(ban_members=True)
async def unban(ctx, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    # Procuring the list of banned members and splitting them by their discriminator tag.

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return
        # Unbanning the banned user.


bot.run(bot.config_token)
# Runs our bot
