"""基于 httpx 的共享连接池 HTTP 客户端。

对外暴露一个与 `requests.post` 兼容签名的模块级函数：

    post(url, headers=None, json=None, timeout=None, stream=False)

- 非流式：直接返回 `httpx.Response`（其 `status_code` / `json()` / `text`
  与 `requests.Response` 兼容），调用点逻辑无需改动。
- 流式：返回一个 requests 风格的包装对象 `_StreamResponse`，支持
  `status_code` / `text` / 可写属性 `encoding` / `iter_lines(decode_unicode=True)`，
  内部基于 httpx 的流式接口实现，并在迭代结束或异常时正确关闭底层流。

模块级单例客户端启用 keep-alive 连接复用与连接上限，避免每次请求重新建连，
从而削减单次调用延迟。可选启用 HTTP/2：仅在安装了 h2 时开启，否则自动降级
到 HTTP/1.1。

`requests` 仍被 frontend_server 等其它模块使用，彼此互不冲突。
"""

import logging

import httpx

logger = logging.getLogger(__name__)


# 默认超时：连接 10s，读/写/池超时统一为 120s（与调用点 timeout=120 兼容）。
_DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=120.0, write=120.0, pool=10.0)

# 共享连接池：限制连接上限并开启 keep-alive 复用。
_LIMITS = httpx.Limits(
    max_keepalive_connections=20,
    max_connections=100,
    keepalive_expiry=30.0,
)

# 可选 HTTP/2：仅当安装了 h2 时启用；缺失则降级为 HTTP/1.1（不报错）。
try:  # pragma: no cover - 依赖环境是否安装 h2
    import h2  # noqa: F401

    _HTTP2 = True
except Exception:  # noqa: BLE001 - h2 缺失属正常降级
    _HTTP2 = False


def _build_client():
    """构建模块级共享客户端（连接池 + keep-alive + 可选 HTTP/2）。"""
    return httpx.Client(
        limits=_LIMITS,
        timeout=_DEFAULT_TIMEOUT,
        http2=_HTTP2,
        follow_redirects=True,
    )


# 模块级单例客户端：所有调用点共享同一连接池。
_CLIENT = _build_client()


def _normalize_timeout(timeout):
    """把调用点传入的 timeout（秒，如 120/15）转换为 httpx.Timeout。

    未传入时回退默认超时；连接超时取 10s 与传入值的较小者，避免长读超时下
    连接阶段也长时间挂起。
    """
    if timeout is None:
        return _DEFAULT_TIMEOUT
    try:
        value = float(timeout)
    except (TypeError, ValueError):
        return _DEFAULT_TIMEOUT
    if value <= 0:
        return _DEFAULT_TIMEOUT
    return httpx.Timeout(value, connect=min(10.0, value))


class _StreamResponse:
    """将 httpx 流式响应包装为 requests 风格，供 `stream_generator` 消费。

    - `status_code`：响应状态码；
    - `text`：惰性读取完整响应体（读取后自动关闭底层流）；
    - `encoding`：可写属性，影响 `iter_lines` / `text` 的字节解码；
    - `iter_lines(decode_unicode=True)`：逐行 yield str，迭代结束或异常时关闭流。
    """

    def __init__(self, response, ctx):
        self._response = response
        self._ctx = ctx
        self.status_code = response.status_code
        # 默认按 utf-8 解码；调用点会显式覆盖为 'utf-8'
        self.encoding = 'utf-8'
        self._text = None
        self._closed = False

    def iter_lines(self, decode_unicode=True):
        """逐行返回响应内容；迭代结束（或异常）时关闭底层流。"""
        try:
            for line in self._response.iter_lines():
                if decode_unicode and isinstance(line, bytes):
                    line = line.decode(self.encoding or 'utf-8', errors='replace')
                yield line
        finally:
            self.close()

    @property
    def text(self):
        """惰性读取完整响应体；读完后关闭底层流。"""
        if self._text is None:
            try:
                raw = self._response.read()
                if isinstance(raw, bytes):
                    self._text = raw.decode(self.encoding or 'utf-8', errors='replace')
                else:
                    self._text = raw
            except Exception:  # noqa: BLE001 - 读取失败统一降级为空串
                self._text = ''
            finally:
                self.close()
        return self._text

    def close(self):
        """关闭底层流（幂等）。"""
        if self._closed:
            return
        self._closed = True
        try:
            self._ctx.__exit__(None, None, None)
        except Exception:  # noqa: BLE001 - 关闭失败不影响调用方
            pass
        try:
            self._response.close()
        except Exception:  # noqa: BLE001
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def post(url, headers=None, json=None, timeout=None, stream=False):
    """与 `requests.post` 兼容签名的请求函数（共享连接池）。

    Args:
        url: 目标 URL
        headers: 请求头 dict
        json: JSON 请求体（httpx 负责序列化并设置 Content-Type）
        timeout: 超时秒数（调用点传 120 或 15）
        stream: True 时返回 requests 风格的流式包装对象，否则返回 httpx.Response
    """
    if stream:
        # 手动进入 httpx 的流式上下文：返回包装对象，由消费方在迭代结束时关闭。
        ctx = _CLIENT.stream(
            "POST", url, headers=headers, json=json,
            timeout=_normalize_timeout(timeout),
        )
        response = ctx.__enter__()
        return _StreamResponse(response, ctx)
    return _CLIENT.post(
        url, headers=headers, json=json, timeout=_normalize_timeout(timeout)
    )


def get_client():
    """返回底层共享 httpx 客户端（便于测试检查连接池统计）。"""
    return _CLIENT


def close():
    """关闭共享客户端（释放连接池）。"""
    try:
        _CLIENT.close()
    except Exception:  # noqa: BLE001
        pass


def reset():
    """重建共享客户端（测试隔离 / 清理用）：关闭旧客户端并新建单例。"""
    global _CLIENT
    close()
    _CLIENT = _build_client()
    return _CLIENT
