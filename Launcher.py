from discord.ext import commands
import discord
import asyncio

intents = discord.Intents.all()
TOKEN = 'ODA4MjA0MTU3MzY5NzEyNjYx.YCDIxg.dz1d7xU7ytZQh6F9uKm-g7vSqmI' #TOKENを入力してください
prefix = "/" #お好きなプレフィックス

bot = commands.Bot(command_prefix=prefix,help_command=None,intents=intents)

bot.load_extension("main")

bot.run(TOKEN)