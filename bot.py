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
    # まずはUTF-8で試す
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            channels = [row for row in reader]
    except UnicodeDecodeError:
        # UTF-8で失敗した場合はShift_JISで再試行
        try:
            with open(file_path, 'r', encoding='shift_jis') as f:
                reader = csv.DictReader(f)
                channels = [row for row in reader]
                await interaction.channel.send("Shift_JISでCSVファイルを読み込みました(UTF-8で読み込むことをお勧めします)")
        except Exception as e:
            await interaction.edit(content=f'Error reading CSV file: {e}')
            return
    except Exception as e:
        await interaction.edit(content=f'Error reading CSV file: {e}')
        return

    guild = interaction.guild
    created_channels = 0
    skipped_channels = 0
    category_cache = {}  # カテゴリのキャッシュ

    for row in channels:
        try:
            category_name = row.get('Category Name', '').strip()
            channel_name = row['Channel Name'].strip()
            channel_type = row.get('Channel Type', '').strip()
            role_name = row.get('Role Name', None)  # ロール名はオプション

            # カテゴリの取得または作成
            if category_name:
                if category_name not in category_cache:
                    category = discord.utils.get(guild.categories, name=category_name)
                    if not category:
                        category = await guild.create_category(category_name)
                    category_cache[category_name] = category
                else:
                    category = category_cache[category_name]
            else:
                category = None

            # チャンネルの存在確認
            existing_channel = discord.utils.get(
                guild.channels,
                name=channel_name,
                category=category
            )
            if existing_channel and existing_channel.type == (discord.ChannelType.text if channel_type.lower() == 'text' else discord.ChannelType.voice):
                # チャンネルの名前、カテゴリ、タイプ全て一致している場合にスキップ
                skipped_channels += 1
                continue

            # チャンネルの作成
            if channel_type.lower() == 'text':
                if category:
                    await guild.create_text_channel(channel_name, category=category)
                else:
                    await guild.create_text_channel(channel_name)
                created_channels += 1
            elif channel_type.lower() == 'voice':
                if category:
                    await guild.create_voice_channel(channel_name, category=category)
                else:
                    await guild.create_voice_channel(channel_name)
                created_channels += 1
            else:
                await interaction.edit(content=f'Unsupported channel type: {channel_type}')
                return
        except KeyError as e:
            await interaction.edit(content=f'CSV missing expected column: {e}')
            return
        except Exception as e:
            await interaction.edit(content=f'Error creating channel: {e}')
            return

    await interaction.edit(content=f'{created_channels}個のチャンネルを作成しました（{skipped_channels}個のチャンネルは既に存在するためスキップされました）')

# Botを起動
bot.run(TOKEN)