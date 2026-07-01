import os
import discord
import shlex
from discord.ext import commands
from config import ALLOWED_USER_ID, ZEROG_DIR, AGY_PATH, logger
from core.state import THREAD_MODELS, load_thread_state, save_thread_state
from core.runner import run_agy

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_dir = os.path.join(ZEROG_DIR, "temp")
        os.makedirs(self.temp_dir, exist_ok=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Let the bot process slash commands if any, although discord.py handles slash commands separately.
        # This is just in case we have text commands.
        await self.bot.process_commands(message)

        if isinstance(message.channel, discord.Thread) and message.author.id == ALLOWED_USER_ID:
            if message.content.startswith('/'):
                return
                
            thread = message.channel
            thread_id_str = str(thread.id)
            prompt = message.content

            logger.info(f"📥 [디스코드 입력] 스레드: #{thread.name} | 프롬프트: '{prompt}'")

            # 파일 첨부 처리
            attachment_context = ""
            if message.attachments:
                for attachment in message.attachments:
                    file_path = os.path.join(self.temp_dir, attachment.filename)
                    await attachment.save(file_path)
                    attachment_context += f"[첨부파일 참조: {file_path}]\n"
                    logger.info(f"📎 [첨부파일 저장] {file_path}")
                
                if not prompt:
                    prompt = "첨부된 파일을 확인해주세요."
                    
                prompt = attachment_context + prompt

            async with thread.typing():
                history, bound_dir = load_thread_state(thread_id_str)
                
                context_prompt = ""
                if len(history) > 0:
                    context_prompt = "<CONVERSATION_HISTORY>\n다음은 우리의 이전 전체 대화 기록입니다. 이 맥락을 완벽하게 기억하고 바탕으로 사용자의 새로운 질문/명령에 답변 및 수행하세요.\n\n"
                    for msg in history:
                        context_prompt += f"{msg['role']}: {msg['content']}\n"
                    context_prompt += "</CONVERSATION_HISTORY>\n\n"
                
                # ZeroG 전용 Rules 주입
                zerog_rules = ""
                rules_path = os.path.join(ZEROG_DIR, "AGENTS.md")
                if os.path.exists(rules_path):
                    with open(rules_path, "r", encoding="utf-8") as f:
                        rules_content = f.read().strip()
                        if rules_content:
                            zerog_rules = f"<ZEROG_RULES>\n너는 현재 터미널이 아니라 디스코드 ZeroG 봇에 의해 실행되고 있다. 다음 규칙을 반드시 가장 최우선으로 준수해라:\n\n{rules_content}\n</ZEROG_RULES>\n\n"
                
                full_prompt = context_prompt + zerog_rules + f"<USER_REQUEST>\n{prompt}\n</USER_REQUEST>"
                escaped_prompt = shlex.quote(full_prompt)
                
                base_cmd = f'{AGY_PATH} --print'
                if thread_id_str in THREAD_MODELS:
                    model = THREAD_MODELS[thread_id_str]
                    # 모델명도 안전하게 shlex.quote 사용
                    base_cmd += f' --model {shlex.quote(model)}'
                    
                cmd_str = f'{base_cmd} {escaped_prompt}'
                logger.info(f"⚙️ [실행] agy (프롬프트 길이: {len(full_prompt)}자)")
                if bound_dir:
                    logger.info(f"📁 [바인딩 경로] {bound_dir}")
                
                # Execute agy
                returncode, full_output = await run_agy(thread, cmd_str, cwd=bound_dir)
                
                # Save history on success
                if returncode == 0 and full_output:
                    history.append({"role": "User", "content": prompt})
                    history.append({"role": "Assistant", "content": full_output})
                    save_thread_state(thread_id_str, history, bound_dir)

async def setup(bot):
    await bot.add_cog(ChatCog(bot))
