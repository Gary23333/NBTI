"""会话存储门面。

对外保持既有 API 完全不变（ConversationStore / store / is_valid_conversation_id 等），
内部委托给 nbti.storage 中的 StorageBackend 实现（默认文件后端，可选 Redis 后端）。
"""

import os

from nbti.storage import (
    StorageBackend,
    FileStorage,
    RedisStorage,
    create_store,
    is_valid_conversation_id,
)


class ConversationStore:
    """会话存储门面：委托给 StorageBackend。

    保留 base_dir / lock / _read / _write / cleanup_old 等成员，
    使 app.py 的 ShareStore(ConversationStore) 与 utils.py 的 store.lock/_read/_write 用法无需改动。
    """

    def __init__(self, base_dir, backend=None):
        # backend 可显式注入；否则按 base_dir 走工厂（默认文件后端，环境/配置指定 redis 时才启用）
        if backend is None:
            backend = create_store(base_dir, kind="file")
        self._backend = backend
        # 属性代理：base_dir 与 lock 直接取后端，保证与后端临界区共用同一把锁
        self.base_dir = backend.base_dir
        self.lock = backend.lock

    # ---- 低层读写/清理（委托后端） ----
    def _path(self, conversation_id):
        return self._backend._path(conversation_id)

    def _read(self, conversation_id):
        return self._backend._read(conversation_id)

    def _write(self, conversation_id, data):
        return self._backend._write(conversation_id, data)

    def cleanup_old(self, max_age_hours=24):
        return self._backend.cleanup_old(max_age_hours)

    # ---- 高层业务方法（委托后端） ----
    def get_history(self, conversation_id):
        return self._backend.get_history(conversation_id)

    def save_history(self, conversation_id, history):
        return self._backend.save_history(conversation_id, history)

    def get_scenes(self, conversation_id):
        return self._backend.get_scenes(conversation_id)

    def save_scenes(self, conversation_id, scenes):
        return self._backend.save_scenes(conversation_id, scenes)

    def get_theme(self, conversation_id):
        return self._backend.get_theme(conversation_id)

    def set_theme(self, conversation_id, theme_id):
        return self._backend.set_theme(conversation_id, theme_id)

    def get_style(self, conversation_id):
        return self._backend.get_style(conversation_id)

    def set_style(self, conversation_id, style_name):
        return self._backend.set_style(conversation_id, style_name)

    def get_preload_draft(self, conversation_id, message):
        return self._backend.get_preload_draft(conversation_id, message)

    def save_preload_draft(self, conversation_id, message, answer, tokens_used=0):
        return self._backend.save_preload_draft(conversation_id, message, answer, tokens_used)

    def clear_preloads(self, conversation_id):
        return self._backend.clear_preloads(conversation_id)


store = ConversationStore(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'conversations'))
