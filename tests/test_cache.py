"""进程内 TTL 缓存（nbti/cache.py）测试。

覆盖 TTL 命中/过期、开关关闭语义（get 恒未命中、set 空操作）、set/invalidate/clear、
最大条目驱逐，以及并发写读不崩溃的线程安全。
"""

import os
import sys
import time
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from nbti.cache import Cache, cache_enabled_from_config


# ---------- TTL 命中 / 过期 ----------

class TestCacheTTL:
    def test_hit_within_ttl(self):
        c = Cache(enabled=True, default_ttl=10)
        c.set("k", "v")
        assert c.get("k") == "v"

    def test_miss_for_absent_key(self):
        c = Cache(enabled=True, default_ttl=10)
        assert c.get("never-written") is None

    def test_miss_after_ttl_expiry(self):
        c = Cache(enabled=True, default_ttl=0.05)
        c.set("k", "v")
        time.sleep(0.08)
        assert c.get("k") is None

    def test_ttl_zero_means_no_expiry(self):
        c = Cache(enabled=True, default_ttl=0)
        c.set("k", "v")
        time.sleep(0.05)
        assert c.get("k") == "v"

    def test_explicit_ttl_overrides_default(self):
        c = Cache(enabled=True, default_ttl=100)
        c.set("k", "v", ttl=0.05)
        time.sleep(0.08)
        assert c.get("k") is None


# ---------- 开关关闭时直算（get 未命中 / set 空操作） ----------

class TestCacheDisabled:
    def test_set_is_noop_and_get_misses(self):
        c = Cache(enabled=False)
        c.set("k", "v")
        assert c.get("k") is None
        assert c.stats()["size"] == 0

    def test_toggling_enabled_off_discards_reads(self):
        c = Cache(enabled=True, default_ttl=100)
        c.set("k", "v")
        assert c.get("k") == "v"
        c.enabled = False
        assert c.get("k") is None
        c.enabled = True
        assert c.get("k") == "v"


# ---------- set / invalidate / clear ----------

class TestCacheMutations:
    def test_invalidate_removes_key(self):
        c = Cache(default_ttl=100)
        c.set("k", "v")
        c.invalidate("k")
        assert c.get("k") is None

    def test_invalidate_missing_key_is_noop(self):
        c = Cache(default_ttl=100)
        c.invalidate("nope")  # 不应抛错
        assert c.stats()["size"] == 0

    def test_clear_removes_all(self):
        c = Cache(default_ttl=100)
        for i in range(5):
            c.set(f"k{i}", i)
        c.clear()
        assert all(c.get(f"k{i}") is None for i in range(5))
        assert c.stats()["size"] == 0

    def test_stats_counts_hits_and_misses(self):
        c = Cache(default_ttl=100)
        c.set("k", "v")
        c.get("k")
        c.get("absent")
        s = c.stats()
        assert s["size"] == 1
        assert s["hits"] == 1
        assert s["misses"] == 1
        assert s["enabled"] is True

    def test_max_entries_evicts_oldest_first(self):
        c = Cache(default_ttl=100, max_entries=2)
        c.set("a", 1)
        c.set("b", 2)
        c.set("c", 3)
        assert c.stats()["size"] == 2
        assert c.get("a") is None      # 最早写入被驱逐
        assert c.get("b") == 2
        assert c.get("c") == 3


# ---------- 线程安全 ----------

class TestCacheThreadSafety:
    def test_concurrent_writes_and_reads_do_not_crash(self):
        c = Cache(enabled=True, default_ttl=100, max_entries=200)
        errors = []

        def worker(seed):
            try:
                for i in range(300):
                    key = f"k{(seed * 300 + i) % 64}"
                    c.set(key, i)
                    c.get(key)
                    c.invalidate(f"k{i % 8}")
            except Exception as e:  # noqa: BLE001 — 并发下任何异常都视为失败
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
        c.clear()
        assert c.stats()["size"] == 0


# ---------- 配置驱动开关 ----------

class TestCacheEnabledFromConfig:
    def test_reads_config_flag_false(self, monkeypatch):
        import nbti.config as config_mod
        monkeypatch.setattr(config_mod, "load_config", lambda: {"cache_enabled": False})
        assert cache_enabled_from_config() is False

    def test_reads_config_flag_true(self, monkeypatch):
        import nbti.config as config_mod
        monkeypatch.setattr(config_mod, "load_config", lambda: {"cache_enabled": True})
        assert cache_enabled_from_config() is True

    def test_defaults_true_when_config_unavailable(self, monkeypatch):
        """配置缺失/读取异常时安全降级为默认 True。"""
        import nbti.config as config_mod

        def boom():
            raise RuntimeError("config unavailable")

        monkeypatch.setattr(config_mod, "load_config", boom)
        assert cache_enabled_from_config() is True

    def test_defaults_true_when_key_absent(self, monkeypatch):
        import nbti.config as config_mod
        monkeypatch.setattr(config_mod, "load_config", lambda: {})
        assert cache_enabled_from_config() is True
