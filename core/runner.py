import asyncio
import os
import signal
import tempfile
import discord

ACTIVE_PROCESSES = {}

async def run_agy(thread, cmd_str, cwd=None):
    """
    Runs agy via shell, streams output to the thread status message,
    and returns (returncode, full_output).
    """
    thread_id = str(thread.id)
    
    status_msg = await thread.send("🔄 **작업 시작 중...**")
    
    try:
        process = await asyncio.create_subprocess_shell(
            cmd_str,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd
        )
        ACTIVE_PROCESSES[thread_id] = process

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
        
        # Cleanup
        if thread_id in ACTIVE_PROCESSES:
            del ACTIVE_PROCESSES[thread_id]

        full_output = output_buffer.decode('utf-8', errors='replace').strip()
        
        if process.returncode != 0:
            if process.returncode == -15 or process.returncode == 143: # SIGTERM or killed
                await status_msg.edit(content=f"🛑 **프로세스가 강제 종료되었습니다.**\n{full_output[-1900:]}")
            else:
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
            
        return process.returncode, full_output
        
    except Exception as e:
        print(f"💥 [시스템 오류] {str(e)}")
        await status_msg.edit(content=f"⚠️ 시스템 오류: {str(e)}")
        if thread_id in ACTIVE_PROCESSES:
            del ACTIVE_PROCESSES[thread_id]
        return -1, str(e)

def kill_process(thread_id_str):
    """
    Kills an active process for a given thread ID if it exists.
    Returns True if killed, False otherwise.
    """
    if thread_id_str in ACTIVE_PROCESSES:
        proc = ACTIVE_PROCESSES[thread_id_str]
        try:
            # Terminate the process
            proc.terminate()
            return True
        except Exception as e:
            print(f"Failed to kill process: {e}")
            return False
    return False
