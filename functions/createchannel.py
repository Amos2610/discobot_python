import discord
from discord.ext import commands
import csv

class CreateChannels(commands.Cog):
    """
    Abstract:
    この関数は、CSVファイルからチャンネルを作成するための関数.
    この関数は、/createchannelsコマンドを提供します.
    この関数は、CSVファイルを受け取り、そのファイルに記載されているチャンネルを作成します.
    この関数は、チャンネルの名前、カテゴリ、タイプを指定することができます.
    この関数は、チャンネルの作成に成功した場合、作成したチャンネルの数を返します.
    この関数は、チャンネルの作成に失敗した場合、エラーメッセージを返します.
    """
    def __init__(self, bot):
        self.bot = bot # Botのインスタンス
        # 新しいCSVファイルを読み込むかどうかを示すフラグ(True: 新しいCSVファイルを読み込む, False: 既存のCSVファイルを読み込む)
        self.is_need_csv = False

    @discord.app_commands.command(name="createchannels", description="CSVファイルからチャンネルを作成します")
    async def createchannels(self, interaction: discord.Interaction):
        if self.is_need_csv:
            await interaction.response.send_message("CSVファイルをこのメッセージに返信する形で送信してください。")
        else:
            await self.create_channels_from_csv(interaction, 'csv_files/channels.csv')

    # メッセージを受け取った時の処理
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.is_need_csv and message.attachments:
            file_path = f"./{message.attachments[0].filename}"
            await message.attachments[0].save(file_path)

            interaction = await message.channel.send("チャンネルを作成しています...")
            await self.create_channels_from_csv(interaction, file_path)

    # CSVファイルからチャンネルを作成する
    async def create_channels_from_csv(self, interaction, file_path: str):
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
                await interaction.response.send_message(content=f'Error reading CSV file: {e}')
                return
        except Exception as e:
            await interaction.response.send_message(content=f'Error reading CSV file: {e}')
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
                    await interaction.response.send_message(content=f'Unsupported channel type: {channel_type}')
                    return
            except KeyError as e:
                await interaction.response.send_message(content=f'CSV missing expected column: {e}')
                return
            except Exception as e:
                await interaction.response.send_message(content=f'Error creating channel: {e}')
                return

        await interaction.response.send_message(content=f'{created_channels}個のチャンネルを作成しました（{skipped_channels}個のチャンネルは既に存在するためスキップされました）')

# BotにCogを追加
async def setup(bot):
    await bot.add_cog(CreateChannels(bot))
