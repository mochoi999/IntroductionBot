from discord.ext import commands
import discord

intents = discord.Intents.all()
TOKEN = ''  # TOKENを入力してください
prefix = "/"  # お好きなプレフィックス

bot = commands.Bot(command_prefix=prefix, help_command=None, intents=intents)

bot.load_extension("main")

bot.run(TOKEN)
