import os
import json
import time
import threading
import logging

logger = logging.getLogger(__name__)


class ConversationStore:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.lock = threading.Lock()
        os.makedirs(base_dir, exist_ok=True)

    def get_history(self, conversation_id):
        return self._read(conversation_id).get('history', [])

    def save_history(self, conversation_id, history):
        with self.lock:
            data = self._read(conversation_id)
            data['history'] = history
            self._write(conversation_id, data)

    def get_scenes(self, conversation_id):
        return self._read(conversation_id).get('scenes', [])

    def save_scenes(self, conversation_id, scenes):
        with self.lock:
            data = self._read(conversation_id)
            data['scenes'] = scenes
            self._write(conversation_id, data)

    def get_preload_draft(self, conversation_id, message):
        return self._read(conversation_id).get('preloads', {}).get(message)

    def save_preload_draft(self, conversation_id, message, answer, tokens_used=0):
        with self.lock:
            data = self._read(conversation_id)
            preloads = data.get('preloads', {})
            preloads[message] = {
                "answer": answer,
                "tokens_used": tokens_used,
                "created_at": int(time.time())
            }
            data['preloads'] = preloads
            self._write(conversation_id, data)

    def clear_preloads(self, conversation_id):
        with self.lock:
            data = self._read(conversation_id)
            data['preloads'] = {}
            self._write(conversation_id, data)

    def _read(self, conversation_id):
        path = os.path.join(self.base_dir, f"{conversation_id}.json")
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _write(self, conversation_id, data):
        path = os.path.join(self.base_dir, f"{conversation_id}.json")
        tmp_path = path + ".tmp"
        for attempt in range(3):
            try:
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, path)
                return
            except PermissionError:
                if attempt < 2:
                    time.sleep(0.1 * (attempt + 1))
                else:
                    logger.warning(f"[STORE] 文件写入失败(PermissionError) | id={conversation_id}")

    def cleanup_old(self, max_age_hours=24):
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        for filename in os.listdir(self.base_dir):
            if not filename.endswith('.json'):
                continue
            path = os.path.join(self.base_dir, filename)
            try:
                if now - os.path.getmtime(path) > max_age_seconds:
                    os.remove(path)
            except OSError:
                pass


store = ConversationStore(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'conversations'))
