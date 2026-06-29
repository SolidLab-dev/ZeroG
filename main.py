import discord
from discord.ext import commands
import os
from config import DISCORD_BOT_TOKEN

class ZeroGBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Load Cogs
        await self.load_extension("cogs.commands")
        await self.load_extension("cogs.chat")
        
        # Sync slash commands
        await self.tree.sync()
        print("✅ 슬래시 커맨드가 성공적으로 동기화되었습니다.")

    async def on_ready(self):
        print(f"🚀 에이전트가 준비되었습니다: {self.user.name}")

if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN 환경 변수가 설정되지 않았습니다.")
        exit(1)
        
    bot = ZeroGBot()
    bot.run(DISCORD_BOT_TOKEN)
