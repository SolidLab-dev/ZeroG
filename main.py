import discord
from discord.ext import commands
import os
import sys
from config import DISCORD_BOT_TOKEN, logger
from core.runner import kill_all_processes

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
        try:
            await self.tree.sync()
            logger.info("✅ 슬래시 커맨드가 성공적으로 동기화되었습니다.")
        except Exception as e:
            logger.error(f"❌ 슬래시 커맨드 동기화 실패: {e}")
            
        self.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        logger.error(f"💥 슬래시 커맨드 오류 발생 ({interaction.command.name if interaction.command else 'Unknown'}): {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ 커맨드 실행 중 오류가 발생했습니다. (로그를 확인하세요)", ephemeral=True)

    async def on_command_error(self, ctx, error):
        logger.error(f"💥 커맨드 오류 발생: {error}")
        
    async def close(self):
        logger.info("🛑 봇 종료 요청 수신. 남아있는 서브프로세스를 청소합니다...")
        kill_all_processes()
        await super().close()

    async def on_ready(self):
        logger.info(f"🚀 에이전트가 준비되었습니다: {self.user.name}")

if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        logger.error("❌ DISCORD_BOT_TOKEN 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
        
    bot = ZeroGBot()
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"봇 실행 중 치명적 오류: {e}")
