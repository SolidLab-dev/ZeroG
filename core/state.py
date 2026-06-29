import os
import json
from config import SETTINGS_FILE, THREADS_DIR, logger

THREAD_MODELS = {}

def load_settings():
    global THREAD_MODELS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                THREAD_MODELS = data.get("models", {})
                return
        except Exception as e:
            logger.error(f"⚠️ 설정 로드 실패: {e}")
    THREAD_MODELS = {}

def save_settings():
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"models": THREAD_MODELS}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"⚠️ 설정 저장 실패: {e}")

def load_thread_state(thread_id_str):
    """
    Returns (history: list, bound_dir: str|None)
    """
    history_file = os.path.join(THREADS_DIR, f"{thread_id_str}.json")
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Legacy support: just a history list
                    return data, None
                elif isinstance(data, dict):
                    return data.get("history", []), data.get("bound_dir", None)
        except Exception:
            pass
    return [], None

def save_thread_state(thread_id_str, history, bound_dir=None):
    history_file = os.path.join(THREADS_DIR, f"{thread_id_str}.json")
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({
                "history": history,
                "bound_dir": bound_dir
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"⚠️ 스레드 {thread_id_str} 저장 실패: {e}")

# Load settings at import
load_settings()
