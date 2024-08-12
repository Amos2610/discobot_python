import discord
from discord.ext import commands
import csv
import os
from dotenv import load_dotenv

# 環境変数からトークンを読み込む
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # トークンを取得する

# インテントを定義
intents = discord.Intents.default()
intents.message_content = True

# Botのコマンドプレフィックスを指定し、インテントを渡す
bot = commands.Bot(command_prefix='/', intents=intents)

# is_need_csv 変数を追加（Trueの場合はGoogle SheetsからのCSVを使用、Falseの場合は現在の形）
is_need_csv = True

# ボットが起動した時の処理
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Error syncing commands: {e}')

# /createchannels コマンドを実装
@bot.tree.command(name="createchannels", description="CSVファイルからチャンネルを作成します")
async def createchannels(interaction: discord.Interaction):
    if is_need_csv:
        await interaction.response.send_message("CSVファイルをこのメッセージに返信する形で送信してください。")
    else:
        await create_channels_from_csv(interaction, 'channels.csv')

# メッセージの添付ファイルを受け取るリスナー
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if is_need_csv and message.attachments:
        file_path = f"./{message.attachments[0].filename}"
        await message.attachments[0].save(file_path)

        interaction = await message.channel.send("チャンネルを作成しています...")
        await create_channels_from_csv(interaction, file_path)

async def create_channels_from_csv(interaction, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            channels = [row for row in reader]
    except Exception as e:
        await interaction.edit(content=f'Error reading CSV file: {e}')
        return

    guild = interaction.guild
    created_channels = 0
    for row in channels:
        try:
            category_name = row.get('Category Name')
            channel_name = row['Channel Name']
            channel_type = row.get('Channel Type', '').strip()  # スペースを削除
            role_name = row.get('Role Name')

            existing_channel = discord.utils.get(guild.channels, name=channel_name)
            if existing_channel:
                continue

            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                category = await guild.create_category(category_name)

            if channel_type.lower() == 'text':
                await category.create_text_channel(channel_name)
            elif channel_type.lower() == 'voice':
                await category.create_voice_channel(channel_name)
            else:
                await interaction.edit(content=f'Unsupported channel type: {channel_type}')
                return

            created_channels += 1
        except KeyError as e:
            await interaction.edit(content=f'CSV missing expected column: {e}')
            return

    await interaction.edit(content=f'{created_channels}個のチャンネルを作成しました')

# Botを起動
bot.run(TOKEN)