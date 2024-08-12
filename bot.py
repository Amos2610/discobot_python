import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# 環境変数からトークンを読み込む
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# インテントを定義
intents = discord.Intents.default()
intents.message_content = True

# Botのコマンドプレフィックスを指定し、インテントを渡す
bot = commands.Bot(command_prefix='/', intents=intents)

# Botが起動した時の処理
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        # Cogの読み込み
        await bot.load_extension('functions.createchannel')
        await bot.load_extension('functions.hey')
        synced = await bot.tree.sync()
        print(f"Commands {len(synced)} synced")
    except Exception as e:
        print(f'Error syncing commands: {e}')

# Botを起動
bot.run(TOKEN)
