"""线程安全的 TTL 缓存实现。

供 prompt 构建与会话读缓存复用：
- 支持 get/set/invalidate/clear；
- support enabled 开关（可由配置 cache_enabled 驱动），关闭后 get 恒为未命中、set 为空操作；
- 可选最大条目数上限 + 惰性驱逐（先清过期项，仍超限则按写入顺序驱逐最早条目）。
"""

import time
import logging
import threading

logger = logging.getLogger(__name__)


class Cache:
    """线程安全的 TTL 缓存。

    - get(key)：命中返回缓存值，未命中/过期返回 None（None 视为未命中，请勿缓存 None）；
    - set(key, value, ttl=None)：写入缓存，ttl 为 None 时使用 default_ttl（<=0 表示永不过期）；
    - invalidate(key)：删除单个键；
    - clear()：清空全部；
    - enabled：总开关，False 时 get 不命中、set 不写入。
    """

    def __init__(self, enabled=True, default_ttl=300.0, max_entries=None):
        self.enabled = bool(enabled)
        self.default_ttl = default_ttl
        self.max_entries = max_entries
        # key -> (expire_at | None, value)；dict 天然保持插入顺序，用于惰性驱逐
        self._data = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key):
        """读取缓存；命中返回 value，未命中或已过期返回 None"""
        if not self.enabled:
            return None
        now = time.time()
        with self._lock:
            item = self._data.get(key)
            if item is None:
                self._misses += 1
                return None
            expire_at, value = item
            if expire_at is not None and expire_at <= now:
                # 惰性驱逐已过期项
                self._data.pop(key, None)
                self._misses += 1
                return None
            self._hits += 1
            return value

    def set(self, key, value, ttl=None):
        """写入缓存；ttl 为 None 时使用 default_ttl，ttl<=0 表示永不过期"""
        if not self.enabled:
            return
        if ttl is None:
            ttl = self.default_ttl
        expire_at = None if (ttl is None or ttl <= 0) else time.time() + ttl
        with self._lock:
            self._data[key] = (expire_at, value)
            self._evict_locked()

    def invalidate(self, key):
        """删除指定 key 的缓存项"""
        with self._lock:
            self._data.pop(key, None)

    def clear(self):
        """清空全部缓存项"""
        with self._lock:
            self._data.clear()

    def _evict_locked(self):
        """在持锁状态下做惰性驱逐：先清过期项，仍超上限则按写入顺序淘汰最早条目"""
        if not self.max_entries or len(self._data) <= self.max_entries:
            return
        now = time.time()
        expired = [k for k, (exp, _) in self._data.items() if exp is not None and exp <= now]
        for k in expired:
            self._data.pop(k, None)
        while self.max_entries and len(self._data) > self.max_entries:
            oldest = next(iter(self._data))
            self._data.pop(oldest, None)

    def stats(self):
        """返回缓存统计（便于调试观测）"""
        with self._lock:
            return {
                "size": len(self._data),
                "hits": self._hits,
                "misses": self._misses,
                "enabled": self.enabled,
            }


def cache_enabled_from_config(default=True):
    """从配置读取 cache_enabled 开关。

    缺失键或读取失败（含 config 模块部分初始化导致的循环导入）均返回 default（默认 True）。
    采用惰性导入 config，避免在 config/prompts 模块初始化期间形成硬依赖或循环导入错误。
    """
    try:
        from nbti.config import load_config
        config = load_config()
        if isinstance(config, dict):
            return bool(config.get('cache_enabled', default))
    except Exception as e:  # noqa: BLE001 — 配置不可用时必须安全降级
        logger.debug(f"[CACHE] 读取 cache_enabled 配置失败，使用默认值 {default}: {e}")
    return default
