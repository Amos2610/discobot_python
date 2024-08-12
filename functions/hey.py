import discord
from discord.ext import commands

class Hey(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="hey", description="あいさつに反応してbotが返事します")
    async def hey(self, interaction: discord.Interaction):
        await interaction.response.send_message("こんにちは！")

async def setup(bot):
    await bot.add_cog(Hey(bot))
