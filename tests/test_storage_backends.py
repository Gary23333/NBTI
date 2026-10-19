"""存储后端（nbti/storage.py）测试。

- FileStorage：历史/场景/主题/风格/预载读写、清理、非法 id 校验；
- RedisStorage：用内存假 redis client（注入）验证与文件后端行为等价，不依赖真实 redis 服务；
- create_store：未安装 redis / 未启用时安全回退 FileStorage。
"""

import os
import sys
import time
import types
import fnmatch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nbti.storage import (
    FileStorage, RedisStorage, create_store, is_valid_conversation_id,
)


# ---------------------------------------------------------------------------
# 内存假 redis（最小实现 RedisStorage 依赖的 API 子集）
# ---------------------------------------------------------------------------
class FakeWatchError(Exception):
    """占位 WatchError：_update 的 except 分支才会取到，无冲突时不触发。"""


class FakePipeline:
    """内存版 pipeline：支持 watch/get/multi/set/execute/reset。"""

    def __init__(self, store):
        self._store = store
        self._ops = []
        self._buffering = False

    def watch(self, *keys):
        return True

    def get(self, key):
        return self._store.get(key)

    def multi(self):
        self._buffering = True
        self._ops = []
        return self

    def set(self, key, value):
        if self._buffering:
            self._ops.append((key, value))
        else:
            self._store[key] = value
        return self

    def execute(self):
        for k, v in self._ops:
            self._store[k] = v
        self._ops = []
        self._buffering = False
        return True

    def reset(self):
        self._ops = []
        self._buffering = False


class FakeRedisClient:
    """内存版 redis client：以 dict 为后端，等价 RedisStorage 所依赖的键值语义。"""

    def __init__(self):
        self.store = {}

    def pipeline(self):
        return FakePipeline(self.store)

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value):
        self.store[key] = value

    def delete(self, *keys):
        removed = 0
        for k in keys:
            if k in self.store:
                del self.store[k]
                removed += 1
        return removed

    def scan_iter(self, match=None):
        for key in list(self.store.keys()):
            if match is None or fnmatch.fnmatchcase(key, match):
                yield key


FAKE_REDIS_MOD = types.SimpleNamespace(WatchError=FakeWatchError)


def make_redis_store(tmp_path):
    """构造注入假 client 的 RedisStorage（无需真实 redis 服务/包）。"""
    client = FakeRedisClient()
    store = RedisStorage(str(tmp_path / "conv"), client=client, redis_mod=FAKE_REDIS_MOD)
    return store, client


# ---------------------------------------------------------------------------
# FileStorage
# ---------------------------------------------------------------------------
class TestFileStorage:
    def test_history_roundtrip(self, tmp_path):
        fs = FileStorage(str(tmp_path / "conv"))
        fs.save_history("c1", [{"role": "user", "content": "hi"}])
        assert fs.get_history("c1") == [{"role": "user", "content": "hi"}]

    def test_history_defaults_empty_for_missing(self, tmp_path):
        fs = FileStorage(str(tmp_path / "conv"))
        assert fs.get_history("missing") == []

    def test_scenes_theme_style_roundtrip(self, tmp_path):
        fs = FileStorage(str(tmp_path / "conv"))
        fs.save_scenes("c1", ["s1", "s2"])
        assert fs.get_scenes("c1") == ["s1", "s2"]
        assert fs.get_theme("c1") == "workplace"        # 缺失默认
        fs.set_theme("c1", "love")
        assert fs.get_theme("c1") == "love"
        assert fs.get_style("c1") == "暴躁老油条"        # 缺失默认
        fs.set_style("c1", "玄学算命")
        assert fs.get_style("c1") == "玄学算命"

    def test_preload_draft_roundtrip_and_clear(self, tmp_path):
        fs = FileStorage(str(tmp_path / "conv"))
        fs.save_preload_draft("c1", "msg", "ANSWER", tokens_used=7)
        draft = fs.get_preload_draft("c1", "msg")
        assert draft["answer"] == "ANSWER"
        assert draft["tokens_used"] == 7
        assert "created_at" in draft
        fs.clear_preloads("c1")
        assert fs.get_preload_draft("c1", "msg") is None

    def test_partial_writes_merge_into_same_record(self, tmp_path):
        """多次部分写入应合并到同一记录，互不覆盖。"""
        fs = FileStorage(str(tmp_path / "conv"))
        fs.save_history("c1", [1, 2])
        fs.set_theme("c1", "money")
        fs.save_preload_draft("c1", "m", "a")
        data = fs._read("c1")
        assert data["history"] == [1, 2]
        assert data["theme"] == "money"
        assert data["preloads"]["m"]["answer"] == "a"

    @pytest.mark.parametrize("cid", ["../etc/passwd", "a/b", "has space", "", "x" * 65, "a.b"])
    def test_invalid_conversation_id_rejected(self, tmp_path, cid):
        fs = FileStorage(str(tmp_path / "conv"))
        with pytest.raises(ValueError):
            fs.save_history(cid, [])
        assert not is_valid_conversation_id(cid)

    def test_cleanup_old_removes_stale_files(self, tmp_path):
        fs = FileStorage(str(tmp_path / "conv"))
        fs.save_history("fresh", [])
        fs.save_history("stale", [])
        stale_path = os.path.join(fs.base_dir, "stale.json")
        old = time.time() - 25 * 3600
        os.utime(stale_path, (old, old))

        removed = fs.cleanup_old(24)
        assert removed == 1
        assert not os.path.exists(stale_path)
        assert fs.get_history("fresh") == []


# ---------------------------------------------------------------------------
# RedisStorage（注入内存假 client）：与文件后端行为等价
# ---------------------------------------------------------------------------
class TestRedisStorageEquivalence:
    def test_history_equivalent(self, tmp_path):
        fs = FileStorage(str(tmp_path / "fs"))
        rs, _ = make_redis_store(tmp_path)
        history = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "yo"}]
        fs.save_history("c1", history)
        rs.save_history("c1", history)
        assert fs.get_history("c1") == rs.get_history("c1") == history

    def test_scenes_theme_style_equivalent(self, tmp_path):
        fs = FileStorage(str(tmp_path / "fs"))
        rs, _ = make_redis_store(tmp_path)
        for st in (fs, rs):
            st.save_scenes("c1", ["a", "b"])
            st.set_theme("c1", "love")
            st.set_style("c1", "霸总文学")
        assert rs.get_scenes("c1") == fs.get_scenes("c1") == ["a", "b"]
        assert rs.get_theme("c1") == fs.get_theme("c1") == "love"
        assert rs.get_style("c1") == fs.get_style("c1") == "霸总文学"

    def test_defaults_equivalent_for_missing(self, tmp_path):
        fs = FileStorage(str(tmp_path / "fs"))
        rs, _ = make_redis_store(tmp_path)
        assert rs.get_history("none") == fs.get_history("none") == []
        assert rs.get_scenes("none") == fs.get_scenes("none") == []
        assert rs.get_theme("none") == fs.get_theme("none") == "workplace"
        assert rs.get_style("none") == fs.get_style("none") == "暴躁老油条"

    def test_preload_draft_and_clear_equivalent(self, tmp_path):
        fs = FileStorage(str(tmp_path / "fs"))
        rs, _ = make_redis_store(tmp_path)
        for st in (fs, rs):
            st.save_preload_draft("c1", "msg", "ANS", tokens_used=5)
        fd = fs.get_preload_draft("c1", "msg")
        rd = rs.get_preload_draft("c1", "msg")
        assert fd["answer"] == rd["answer"] == "ANS"
        assert fd["tokens_used"] == rd["tokens_used"] == 5
        for st in (fs, rs):
            st.clear_preloads("c1")
        assert rs.get_preload_draft("c1", "msg") is None
        assert fs.get_preload_draft("c1", "msg") is None

    def test_partial_writes_merge_equivalent(self, tmp_path):
        fs = FileStorage(str(tmp_path / "fs"))
        rs, _ = make_redis_store(tmp_path)
        for st in (fs, rs):
            st.save_history("c1", [1])
            st.set_theme("c1", "money")
            st.save_preload_draft("c1", "m", "a")
        assert rs.get_history("c1") == fs.get_history("c1") == [1]
        assert rs.get_theme("c1") == fs.get_theme("c1") == "money"

    def test_cleanup_old_removes_stale_only(self, tmp_path):
        rs, client = make_redis_store(tmp_path)
        rs.save_history("fresh", [])
        rs.save_history("stale", [])
        # 手动回拨 stale 的写入时间戳（模拟 25 小时前的记录）
        client.store[f"{rs._prefix}stale:ts"] = str(int(time.time() - 25 * 3600))

        removed = rs.cleanup_old(24)
        assert removed == 1
        assert client.get(f"{rs._prefix}stale") is None
        assert rs.get_history("fresh") == []

    def test_constructor_default_client_unchanged(self, tmp_path, monkeypatch):
        """未注入 client 时仍走「惰性导入 redis + 连接自检」原路径（注入设计不改变默认语义）。"""
        import nbti.storage as storage_mod

        client = FakeRedisClient()
        calls = {}

        def fake_create(redis_url):
            calls['url'] = redis_url
            return FAKE_REDIS_MOD, client

        monkeypatch.setattr(storage_mod, "_create_redis_client", fake_create)
        rs = storage_mod.RedisStorage(str(tmp_path / "conv"), redis_url="redis://example/0")
        assert rs._client is client
        assert rs._redis is FAKE_REDIS_MOD
        assert calls['url'] == "redis://example/0"


# ---------------------------------------------------------------------------
# create_store 工厂：安全回退
# ---------------------------------------------------------------------------
class TestCreateStoreFallback:
    def test_default_returns_file_backend(self, tmp_path, monkeypatch):
        monkeypatch.delenv("NBTI_STORAGE_BACKEND", raising=False)
        monkeypatch.delenv("NBTI_REDIS_URL", raising=False)
        store = create_store(str(tmp_path / "conv"))
        assert isinstance(store, FileStorage)

    def test_explicit_redis_kind_falls_back_when_unavailable(self, tmp_path, monkeypatch):
        """显式 kind='redis'：redis 包缺失或连接失败时回退文件后端，绝不抛错。"""
        monkeypatch.delenv("NBTI_STORAGE_BACKEND", raising=False)
        store = create_store(str(tmp_path / "conv"), kind="redis")
        assert isinstance(store, FileStorage)

    def test_env_redis_falls_back_when_unavailable(self, tmp_path, monkeypatch):
        monkeypatch.setenv("NBTI_STORAGE_BACKEND", "redis")
        store = create_store(str(tmp_path / "conv"))
        assert isinstance(store, FileStorage)

    def test_explicit_file_kind_returns_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("NBTI_STORAGE_BACKEND", raising=False)
        store = create_store(str(tmp_path / "conv"), kind="file")
        assert isinstance(store, FileStorage)
