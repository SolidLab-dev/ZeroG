import os
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import tempfile
import json

load_dotenv()

ZEROG_DIR = os.path.expanduser("~/.zerog")
THREADS_DIR = os.path.join(ZEROG_DIR, "threads")
os.makedirs(THREADS_DIR, exist_ok=True)
SETTINGS_FILE = os.path.join(ZEROG_DIR, "settings.json")

def load_settings():
    global THREAD_MODELS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                THREAD_MODELS = data.get("models", {})
                return
        except Exception as e:
            print(f"⚠️ 설정 로드 실패: {e}")
    THREAD_MODELS = {}

def save_settings():
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"models": THREAD_MODELS}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 설정 저장 실패: {e}")

def load_thread_history(thread_id_str):
    history_file = os.path.join(THREADS_DIR, f"{thread_id_str}.json")
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_thread_history(thread_id_str, history):
    history_file = os.path.join(THREADS_DIR, f"{thread_id_str}.json")
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 스레드 {thread_id_str} 저장 실패: {e}")

class ZeroGBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = ZeroGBot()

ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))

# 동적 모델 목록 캐시
AVAILABLE_MODELS = ["Gemini 3.5 Flash (High)"]

# 전역 딕셔너리 선언 및 로드
THREAD_MODELS = {}
load_settings()

@bot.event
async def on_ready():
    global AVAILABLE_MODELS
    print(f"🚀 에이전트가 준비되었습니다: {bot.user.name}")
    print("✅ 슬래시 커맨드가 성공적으로 동기화되었습니다.")
    
    # 봇 시작 시 사용 가능한 모델 목록 로드
    print("🔄 agy 사용 가능한 모델 목록을 불러오는 중...")
    try:
        proc = await asyncio.create_subprocess_shell("agy models", stdout=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        lines = stdout.decode('utf-8').strip().split('\n')
        models = []
        for line in lines:
            line = line.strip()
            # 마크다운 리스트(*) 형식이나 일반 텍스트에서 모델명 추출
            if line and not "Available" in line and not "===" in line:
                model_name = line.lstrip("* -").strip()
                if model_name:
                    models.append(model_name)
                    
        if models:
            AVAILABLE_MODELS = models
            print(f"✅ 사용 가능한 모델 {len(models)}개를 성공적으로 로드했습니다.")
        else:
            print("⚠️ 모델 목록이 비어있습니다. 기본값을 사용합니다.")
    except Exception as e:
        print(f"⚠️ 모델 목록을 가져오는 데 실패했습니다: {e}")

async def model_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    # 사용자가 입력 중인 텍스트와 매칭되는 모델 반환 (최대 25개)
    matches = [
        app_commands.Choice(name=model, value=model)
        for model in AVAILABLE_MODELS if current.lower() in model.lower()
    ]
    return matches[:25]

@bot.tree.command(name="model", description="현재 태스크 스레드에서 사용할 agy 모델을 설정합니다.")
@app_commands.describe(model_name="사용할 모델을 검색하거나 선택하세요")
@app_commands.autocomplete(model_name=model_autocomplete)
async def set_model(interaction: discord.Interaction, model_name: str = None):
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

@bot.tree.command(name="create", description="외출 중 아이폰에서 새로운 개발 태스크 스레드를 생성합니다.")
@app_commands.describe(task_name="생성할 태스크의 이름을 입력하세요 (선택사항)")
async def create_task(interaction: discord.Interaction, task_name: str = None):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("❌ 권한이 없습니다.", ephemeral=True)
        return

    if not task_name:
        current_time = datetime.now().strftime("%m%d-%H%M")
        task_name = f"태스크-{current_time}"

    await interaction.response.send_message(f"🛠️ **새로운 개발 태스크 생성:** `{task_name}`\n스레드에서 컨텍스트를 유지하며 대화를 시작합니다.")
    init_msg = await interaction.original_response()
    thread = await init_msg.create_thread(name=f"task-{task_name[:20]}", auto_archive_duration=60)
    
    # 스레드 생성 시 해당 스레드의 대화 기록 초기화
    # 스레드 생성 시 해당 스레드의 대화 기록 초기화 파일 생성
    save_thread_history(str(thread.id), [])
    await thread.send("👋 안녕하세요! 이 스레드에서 내리는 명령은 맥북의 `agy` CLI로 전달됩니다. 스레드 문맥(Context)이 안전하게 유지됩니다.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if isinstance(message.channel, discord.Thread) and message.author.id == ALLOWED_USER_ID:
        if message.content.startswith('/'):
            return
            
        thread = message.channel
        prompt = message.content

        print(f"\n📥 [디스코드 입력] 스레드: #{thread.name} | 프롬프트: '{prompt}'")

        async with thread.typing():
            try:
                thread_id_str = str(thread.id)
                history = load_thread_history(thread_id_str)
                
                # 무제한 토큰 및 100만 이상의 컨텍스트 윈도우를 활용하여 요약 없이 모든 기록을 영구 보존
                context_prompt = ""
                if len(history) > 0:
                    context_prompt = "다음은 우리의 이전 전체 대화 기록입니다. 이 맥락을 완벽하게 기억하고 바탕으로 사용자의 새로운 질문/명령에 답변 및 수행하세요.\n\n[이전 대화 기록]\n"
                    for msg in history:
                        context_prompt += f"{msg['role']}: {msg['content']}\n"
                    context_prompt += "\n[새로운 사용자 명령]: "
                
                full_prompt = context_prompt + prompt
                escaped_prompt = full_prompt.replace('"', '\\"')
                
                base_cmd = 'agy --print'
                
                if thread_id_str in THREAD_MODELS:
                    model = THREAD_MODELS[thread_id_str]
                    base_cmd += f' --model "{model}"'
                    
                cmd = f'{base_cmd} "{escaped_prompt}"'
                print(f"⚙️ [실행] {cmd}")
                
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT
                )
                
                status_msg = await thread.send("🔄 **작업 시작 중...**")
                
                output_buffer = bytearray()
                is_running = True
                
                async def update_message():
                    last_text = ""
                    while is_running:
                        await asyncio.sleep(2)
                        if len(output_buffer) > 0:
                            current_text = output_buffer.decode('utf-8', errors='replace').strip()
                            if current_text and current_text != last_text:
                                display_text = current_text
                                if len(display_text) > 1900:
                                    display_text = "...\n" + display_text[-1900:]
                                
                                try:
                                    await status_msg.edit(content=display_text)
                                    last_text = current_text
                                except discord.errors.HTTPException:
                                    pass
                                
                updater_task = asyncio.create_task(update_message())
                
                while True:
                    chunk = await process.stdout.read(64)
                    if not chunk:
                        break
                    
                    output_buffer.extend(chunk)
                    print(chunk.decode('utf-8', errors='replace'), end="", flush=True)
                
                is_running = False
                await updater_task
                
                await process.wait()
                print(f"\n🏁 [종료] agy 프로세스 종료 (코드: {process.returncode})")
                
                full_output = output_buffer.decode('utf-8', errors='replace').strip()

                # 성공적으로 답변을 받았으면 히스토리에 기록 추가
                if process.returncode == 0 and full_output:
                    history.append({"role": "User", "content": prompt})
                    history.append({"role": "Assistant", "content": full_output})
                    save_thread_history(thread_id_str, history)

                if process.returncode != 0:
                    await status_msg.edit(content=f"❌ **agy 실행 에러 (코드: {process.returncode}):**\n```bash\n{full_output[-1900:]}\n```")
                elif full_output:
                    if len(full_output) > 1900:
                        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".md") as tmp:
                            tmp.write(full_output)
                            tmp_path = tmp.name
                        await status_msg.edit(content="✅ **결과가 길어 파일로 첨부합니다.** (아래 파일 확인)")
                        await thread.send(file=discord.File(tmp_path, filename="result.md"))
                        os.remove(tmp_path)
                    else:
                        await status_msg.edit(content=f"✅ **작업 완료:**\n{full_output}")
                else:
                    await status_msg.edit(content="✅ agy가 작업을 수행했으나 출력된 텍스트가 없습니다.")

            except Exception as e:
                print(f"💥 [시스템 오류] {str(e)}")
                await thread.send(f"⚠️ 시스템 오류: {str(e)}")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
