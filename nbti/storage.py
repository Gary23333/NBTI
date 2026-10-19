"""存储后端解耦：会话/快照存储的后端抽象与实现。

- StorageBackend：后端抽象接口，低层 _read/_write/cleanup_old 由子类实现，高层业务方法提供通用实现；
- FileStorage：文件 JSON 后端，与既有行为完全等价（原子写 + PermissionError 重试 + 非法 id 校验 +
  cleanup_old 按 mtime 清理），并附带「读缓存 + 写时失效」；
- RedisStorage：可选 Redis 后端，仅在显式配置时启用，redis 包惰性导入，未安装/未启用自动回退文件后端；
- create_store：工厂函数，按环境变量/配置解析后端类型并安全回退。
"""

import os
import re
import json
import time
import uuid
import logging
import threading

from nbti.cache import Cache, cache_enabled_from_config

logger = logging.getLogger(__name__)

# conversation_id 合法字符集：字母/数字/下划线/连字符，最长 64（显式拒绝 .. / \ 等路径穿越字符）
_CONV_ID_RE = re.compile(r'^[A-Za-z0-9_-]{1,64}$')

# 会话读缓存默认参数：短 TTL，保证同一会话短时间多次读取命中
_DEFAULT_READ_CACHE_TTL = 30.0
_DEFAULT_READ_CACHE_MAX_ENTRIES = 4096


def is_valid_conversation_id(cid):
    """校验 conversation_id 是否合法（防路径穿越）"""
    return isinstance(cid, str) and bool(_CONV_ID_RE.match(cid))


def _read_cache_enabled_from_config():
    """读取读缓存开关（cache_enabled 配置驱动，缺失默认 True）"""
    try:
        return cache_enabled_from_config()
    except Exception:  # noqa: BLE001 — 任何异常都安全降级为启用
        return True


class StorageBackend:
    """存储后端抽象接口。

    约定：
    - 子类必须实现 _read/_write/cleanup_old；
    - _read/_write 以「整条记录 dict」为粒度（dict 进 / dict 出），确保任意后端都能支撑 ShareStore 的快照读写；
    - 高层业务方法（history/scenes/theme/style/preloads/snapshot）在此提供基于 _read/_write 的通用实现。
    """

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.lock = threading.Lock()

    # ---- 低层接口（子类实现） ----
    def _read(self, conversation_id):
        raise NotImplementedError

    def _write(self, conversation_id, data):
        raise NotImplementedError

    def cleanup_old(self, max_age_hours=24):
        raise NotImplementedError

    # ---- 高层业务方法（通用实现） ----
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

    def get_theme(self, conversation_id):
        return self._read(conversation_id).get('theme', 'workplace')

    def set_theme(self, conversation_id, theme_id):
        with self.lock:
            data = self._read(conversation_id)
            data['theme'] = theme_id
            self._write(conversation_id, data)

    def get_style(self, conversation_id):
        return self._read(conversation_id).get('style', '暴躁老油条')

    def set_style(self, conversation_id, style_name):
        with self.lock:
            data = self._read(conversation_id)
            data['style'] = style_name
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

    # 快照（分享）读写：整体读写一条记录，供 ShareStore 复用
    def save_snapshot(self, share_id, snapshot):
        with self.lock:
            self._write(share_id, snapshot)

    def get_snapshot(self, share_id):
        data = self._read(share_id)
        return data or None


class FileStorage(StorageBackend):
    """文件 JSON 后端：与既有 ConversationStore 文件行为完全等价，并加入读缓存 + 写时失效。"""

    def __init__(self, base_dir, use_cache=True,
                 cache_ttl=_DEFAULT_READ_CACHE_TTL,
                 cache_max_entries=_DEFAULT_READ_CACHE_MAX_ENTRIES):
        super().__init__(base_dir)
        os.makedirs(base_dir, exist_ok=True)
        # 读缓存开关由配置 cache_enabled 驱动（缺失默认 True）；use_cache=False 可强制关闭
        self._read_cache = Cache(
            enabled=bool(use_cache) and _read_cache_enabled_from_config(),
            default_ttl=cache_ttl,
            max_entries=cache_max_entries,
        )

    def _path(self, conversation_id):
        """拼接会话文件路径，非法 id 抛 ValueError（防路径穿越）"""
        if not is_valid_conversation_id(conversation_id):
            raise ValueError(f"非法 conversation_id: {conversation_id!r}")
        return os.path.join(self.base_dir, f"{conversation_id}.json")

    def _read(self, conversation_id):
        # 读缓存命中直接返回；未命中（或已过期）再落盘解析
        cached = self._read_cache.get(conversation_id)
        if cached is not None:
            return cached
        path = self._path(conversation_id)
        data = {}
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError, OSError):
                data = {}
        self._read_cache.set(conversation_id, data)
        return data

    def _write(self, conversation_id, data):
        path = self._path(conversation_id)
        tmp_path = path + ".tmp"
        try:
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
        finally:
            # 写时失效：无论成功/失败都清掉该会话读缓存，保证后续读到最新落盘数据
            self._read_cache.invalidate(conversation_id)

    def cleanup_old(self, max_age_hours=24):
        """清理超过 max_age_hours 未更新的会话文件，返回删除数量；并清空被清理项的读缓存"""
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        removed = 0
        removed_ids = []
        for filename in os.listdir(self.base_dir):
            if not filename.endswith('.json'):
                continue
            path = os.path.join(self.base_dir, filename)
            try:
                if now - os.path.getmtime(path) > max_age_seconds:
                    os.remove(path)
                    removed += 1
                    removed_ids.append(filename[:-5])  # 去掉 '.json' 后缀得到 conversation_id
            except OSError:
                pass
        for cid in removed_ids:
            self._read_cache.invalidate(cid)
        return removed


def _import_redis():
    """惰性导入 redis 包；未安装时抛 ImportError（由 create_store 捕获并回退文件后端）"""
    import redis  # 局部导入，避免引入硬依赖
    return redis


def _create_redis_client(redis_url):
    """创建并自检 redis 客户端；连接失败会抛异常。redis_url 为空时使用默认连接参数"""
    redis_mod = _import_redis()
    if redis_url:
        client = redis_mod.Redis.from_url(redis_url, decode_responses=True)
    else:
        client = redis_mod.Redis(decode_responses=True)
    client.ping()  # 连接自检：redis 未运行时在此抛错，触发回退
    return redis_mod, client


class RedisStorage(StorageBackend):
    """可选 Redis 后端。

    - 仅在显式配置（环境 NBTI_STORAGE_BACKEND=redis 或 config storage_backend="redis"）时启用；
    - 每条会话以 JSON 字符串存于 Redis（整条记录读写，等价文件后端语义）；
    - 高层「读改写」用 WATCH/MULTI 乐观并发，支持多 worker 并发安全。
    """

    def __init__(self, base_dir, redis_url='', client=None, redis_mod=None):
        super().__init__(base_dir)
        if client is not None:
            # 测试注入路径：直接使用外部提供的（假）redis client，避免依赖真实 redis 包/服务。
            # redis_mod 可选，仅 _update 的 except 分支会取它的 WatchError；无冲突时不会触发。
            # 默认（client=None）行为完全不变：惰性导入 redis 并连接自检。
            self._redis = redis_mod
            self._client = client
        else:
            redis_mod, client = _create_redis_client(redis_url)
            self._redis = redis_mod
            self._client = client
        self._prefix = os.environ.get('NBTI_REDIS_PREFIX', 'nbti:conv:')

    # ---- 键工具 ----
    def _key(self, conversation_id):
        return f"{self._prefix}{conversation_id}"

    def _ts_key(self, conversation_id):
        return f"{self._prefix}{conversation_id}:ts"

    # ---- 低层接口 ----
    def _read(self, conversation_id):
        raw = self._client.get(self._key(conversation_id))
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError, ValueError):
            return {}

    def _write(self, conversation_id, data):
        pipe = self._client.pipeline()
        pipe.set(self._key(conversation_id), json.dumps(data, ensure_ascii=False))
        pipe.set(self._ts_key(conversation_id), str(int(time.time())))
        pipe.execute()

    def _update(self, conversation_id, mutator):
        """乐观并发地读改写：WATCH 后检测冲突则重试，保证多 worker 下不丢更新"""
        key = self._key(conversation_id)
        ts_key = self._ts_key(conversation_id)
        pipe = self._client.pipeline()
        try:
            while True:
                try:
                    pipe.watch(key)
                    raw = pipe.get(key)
                    data = json.loads(raw) if raw else {}
                    mutator(data)
                    pipe.multi()
                    pipe.set(key, json.dumps(data, ensure_ascii=False))
                    pipe.set(ts_key, str(int(time.time())))
                    pipe.execute()
                    return data
                except self._redis.WatchError:
                    continue
        finally:
            pipe.reset()

    def cleanup_old(self, max_age_hours=24):
        """清理超过 max_age_hours 未更新的会话，返回删除数量（基于写入时间戳）"""
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        removed = 0
        for key in self._client.scan_iter(match=f"{self._prefix}*"):
            if key.endswith(':ts'):
                continue
            cid = key[len(self._prefix):]
            ts_raw = self._client.get(self._ts_key(cid))
            try:
                ts = int(ts_raw) if ts_raw else 0
            except (TypeError, ValueError):
                ts = 0
            if ts and now - ts > max_age_seconds:
                self._client.delete(key, self._ts_key(cid))
                removed += 1
        return removed

    # ---- 高层业务方法（Redis 用 _update 保证跨 worker 原子读改写） ----
    def get_history(self, conversation_id):
        return self._read(conversation_id).get('history', [])

    def save_history(self, conversation_id, history):
        with self.lock:
            self._update(conversation_id, lambda d: d.__setitem__('history', history))

    def get_scenes(self, conversation_id):
        return self._read(conversation_id).get('scenes', [])

    def save_scenes(self, conversation_id, scenes):
        with self.lock:
            self._update(conversation_id, lambda d: d.__setitem__('scenes', scenes))

    def get_theme(self, conversation_id):
        return self._read(conversation_id).get('theme', 'workplace')

    def set_theme(self, conversation_id, theme_id):
        with self.lock:
            self._update(conversation_id, lambda d: d.__setitem__('theme', theme_id))

    def get_style(self, conversation_id):
        return self._read(conversation_id).get('style', '暴躁老油条')

    def set_style(self, conversation_id, style_name):
        with self.lock:
            self._update(conversation_id, lambda d: d.__setitem__('style', style_name))

    def get_preload_draft(self, conversation_id, message):
        return self._read(conversation_id).get('preloads', {}).get(message)

    def save_preload_draft(self, conversation_id, message, answer, tokens_used=0):
        def mutator(data):
            preloads = data.get('preloads', {})
            preloads[message] = {
                "answer": answer,
                "tokens_used": tokens_used,
                "created_at": int(time.time())
            }
            data['preloads'] = preloads
        with self.lock:
            self._update(conversation_id, mutator)

    def clear_preloads(self, conversation_id):
        with self.lock:
            self._update(conversation_id, lambda d: d.__setitem__('preloads', {}))


def _read_storage_config():
    """惰性读取存储相关配置（缺失默认 file/空 url）；任何异常都安全降级"""
    try:
        from nbti.config import load_config
        config = load_config()
        if isinstance(config, dict):
            return str(config.get('storage_backend', '') or '').strip().lower(), \
                   str(config.get('redis_url', '') or '').strip()
    except Exception as e:  # noqa: BLE001 — 配置不可用时安全降级
        logger.debug(f"[STORAGE] 读取 storage_backend 配置失败: {e}")
    return '', ''


def _resolve_backend_options(kind, redis_url):
    """解析最终生效的后端类型与 redis_url。

    优先级：显式 kind=="redis" > 环境变量 NBTI_STORAGE_BACKEND > 配置 storage_backend；
    任一为 "redis" 即启用 Redis。redis_url 依次取显式参数、环境变量、配置。
    """
    kind = (kind or 'file').strip().lower() if isinstance(kind, str) else 'file'
    env_kind = (os.environ.get('NBTI_STORAGE_BACKEND') or '').strip().lower()
    env_url = (os.environ.get('NBTI_REDIS_URL') or '').strip()
    cfg_kind, cfg_url = _read_storage_config()
    if kind == 'redis' or env_kind == 'redis' or cfg_kind == 'redis':
        return 'redis', (redis_url or env_url or cfg_url)
    return 'file', (redis_url or env_url or cfg_url)


def create_store(base_dir, kind="file", redis_url=""):
    """存储后端工厂。

    - kind 默认 "file"；环境变量 NBTI_STORAGE_BACKEND / 配置 storage_backend 为 "redis" 时启用 Redis；
    - Redis 不可用（未安装 redis 包 / 显式要求但连接失败）时自动回退 FileStorage，绝不抛错。
    """
    resolved_kind, resolved_url = _resolve_backend_options(kind, redis_url)
    if resolved_kind == 'redis':
        try:
            backend = RedisStorage(base_dir, resolved_url)
            logger.info(f"[STORAGE] 已启用 Redis 后端 | url={resolved_url or '(默认)'}")
            return backend
        except Exception as e:  # noqa: BLE001 — redis 缺失/不可达时回退文件后端
            logger.info(f"[STORAGE] Redis 后端不可用，自动回退文件后端: {e}")
    return FileStorage(base_dir)
