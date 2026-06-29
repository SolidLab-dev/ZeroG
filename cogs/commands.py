import os
import discord
import asyncio
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from config import ALLOWED_USER_ID, AGY_PATH, logger
from core.state import THREAD_MODELS, save_settings, load_thread_state, save_thread_state
from core.runner import kill_process

# Cache for available models
AVAILABLE_MODELS = ["Gemini 3.5 Flash (High)"]

class TaskCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global AVAILABLE_MODELS
        logger.info(f"🔄 {AGY_PATH} 사용 가능한 모델 목록을 불러오는 중...")
        try:
            proc = await asyncio.create_subprocess_shell(f"{AGY_PATH} models", stdout=asyncio.subprocess.PIPE)
            stdout, _ = await proc.communicate()
            lines = stdout.decode('utf-8').strip().split('\n')
            models = []
            for line in lines:
                line = line.strip()
                if line and not "Available" in line and not "===" in line:
                    model_name = line.lstrip("* -").strip()
                    if model_name:
                        models.append(model_name)
                        
            if models:
                AVAILABLE_MODELS = models
                logger.info(f"✅ 사용 가능한 모델 {len(models)}개를 성공적으로 로드했습니다.")
            else:
                logger.warning("⚠️ 모델 목록이 비어있습니다. 기본값을 사용합니다.")
        except Exception as e:
            logger.error(f"⚠️ 모델 목록을 가져오는 데 실패했습니다: {e}")

    async def model_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        matches = [
            app_commands.Choice(name=model, value=model)
            for model in AVAILABLE_MODELS if current.lower() in model.lower()
        ]
        return matches[:25]

    @app_commands.command(name="model", description="현재 태스크 스레드에서 사용할 agy 모델을 설정합니다.")
    @app_commands.describe(model_name="사용할 모델을 검색하거나 선택하세요")
    @app_commands.autocomplete(model_name=model_autocomplete)
    async def set_model(self, interaction: discord.Interaction, model_name: str = None):
        if interaction.user.id != ALLOWED_USER_ID:
            await interaction.response.send_message("❌ 권한이 없습니다.", ephemeral=True)
            return
            
        if not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("⚠️ 모델 설정은 태스크 스레드 내부에서만 가능합니다.", ephemeral=True)
            return
            
        if not model_name:
            current_model = THREAD_MODELS.get(str(interaction.channel_id), "기본 모델 (settings.json 기준)")
            await interaction.response.send_message(f"ℹ️ 현재 스레드의 모델: `{current_model}`\n(선택지에서 모델을 지정해주세요)", ephemeral=True)
            return
            
        THREAD_MODELS[str(interaction.channel_id)] = model_name
        save_settings()
        await interaction.response.send_message(f"✅ 이 스레드의 작동 모델이 `{model_name}`(으)로 설정되었습니다.")

    @app_commands.command(name="create", description="새로운 개발 태스크 스레드를 생성합니다.")
    @app_commands.describe(task_name="생성할 태스크의 이름을 입력하세요 (선택사항)")
    async def create_task(self, interaction: discord.Interaction, task_name: str = None):
        if interaction.user.id != ALLOWED_USER_ID:
            await interaction.response.send_message("❌ 권한이 없습니다.", ephemeral=True)
            return

        if not task_name:
            current_time = datetime.now().strftime("%m%d-%H%M")
            task_name = f"태스크-{current_time}"

        await interaction.response.send_message(f"🛠️ **새로운 개발 태스크 생성:** `{task_name}`\n스레드에서 컨텍스트를 유지하며 대화를 시작합니다.")
        init_msg = await interaction.original_response()
        thread = await init_msg.create_thread(name=f"task-{task_name[:20]}", auto_archive_duration=60)
        
        save_thread_state(str(thread.id), [], None)
        await thread.send("👋 안녕하세요! 이 스레드에서 내리는 명령은 맥북의 `agy` CLI로 전달됩니다. 스레드 문맥(Context)이 안전하게 유지됩니다.")

    @app_commands.command(name="bind", description="이 스레드의 작업 디렉토리를 특정 로컬 경로로 고정합니다.")
    @app_commands.describe(path="고정할 절대 경로 (예: ~/CODE/MyProject)")
    async def bind_dir(self, interaction: discord.Interaction, path: str):
        if interaction.user.id != ALLOWED_USER_ID:
            await interaction.response.send_message("❌ 권한이 없습니다.", ephemeral=True)
            return
            
        if not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("⚠️ 바인딩은 태스크 스레드 내부에서만 가능합니다.", ephemeral=True)
            return
            
        thread_id = str(interaction.channel_id)
        expanded_path = os.path.expanduser(path)
        
        if not os.path.isdir(expanded_path):
            await interaction.response.send_message(f"❌ 해당 경로를 찾을 수 없습니다: `{expanded_path}`", ephemeral=True)
            return
            
        history, _ = load_thread_state(thread_id)
        save_thread_state(thread_id, history, expanded_path)
        
        await interaction.response.send_message(f"📂 **작업 디렉토리 바인딩 완료**\n이 스레드의 모든 명령은 이제 `{expanded_path}`에서 실행됩니다.")

    @app_commands.command(name="kill", description="이 스레드에서 현재 실행 중인 백그라운드 작업을 강제로 종료합니다.")
    async def kill_task(self, interaction: discord.Interaction):
        if interaction.user.id != ALLOWED_USER_ID:
            await interaction.response.send_message("❌ 권한이 없습니다.", ephemeral=True)
            return
            
        if not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("⚠️ 태스크 스레드 내부에서만 사용 가능합니다.", ephemeral=True)
            return
            
        thread_id = str(interaction.channel_id)
        if kill_process(thread_id):
            await interaction.response.send_message("🛑 실행 중인 프로세스를 강제로 종료했습니다.")
        else:
            await interaction.response.send_message("ℹ️ 현재 이 스레드에서 실행 중인 프로세스가 없습니다.", ephemeral=True)
            
    @app_commands.command(name="sh", description="LLM을 거치지 않고 맥북에서 순수 쉘 명령어(Bash/Zsh)를 실행합니다.")
    @app_commands.describe(command="실행할 명령어 (예: ls -la)")
    async def raw_shell(self, interaction: discord.Interaction, command: str):
        if interaction.user.id != ALLOWED_USER_ID:
            await interaction.response.send_message("❌ 권한이 없습니다.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        cwd = None
        if isinstance(interaction.channel, discord.Thread):
            _, bound_dir = load_thread_state(str(interaction.channel_id))
            cwd = bound_dir
            
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=cwd
            )
            stdout, _ = await proc.communicate()
            output = stdout.decode('utf-8', errors='replace').strip()
            
            if not output:
                output = "(출력 없음)"
                
            if len(output) > 1900:
                output = output[-1900:]
                
            await interaction.followup.send(f"💻 **Raw Shell (`{command}`):**\n```bash\n{output}\n```")
        except Exception as e:
            await interaction.followup.send(f"❌ 오류 발생: {e}")

async def setup(bot):
    await bot.add_cog(TaskCommands(bot))
