"""Offline deployment checks; Docker itself is exercised by CI."""

import os
from pathlib import Path
import runpy
import signal
import subprocess
import sys
import time
from unittest.mock import MagicMock

import pytest
import requests

from scripts import healthcheck

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(('status', 'payload', 'expected'), [
    (200, {'status': 'ok'}, True), (500, {'status': 'ok'}, False),
    (503, {'status': 'error'}, False), (302, {'status': 'ok'}, False),
    (200, {'status': 'error'}, False), (200, [], False),
])
def test_healthcheck_requires_success(status, payload, expected, monkeypatch):
    response = MagicMock(status_code=status)
    response.json.return_value = payload
    get = MagicMock(return_value=response)
    monkeypatch.setattr(healthcheck.requests, 'get', get)
    assert healthcheck.healthy() is expected
    get.assert_called_once_with('http://127.0.0.1:8080/api/health', timeout=3, allow_redirects=False)
    response.close.assert_called_once()


@pytest.mark.parametrize('error', [requests.Timeout(), requests.ConnectionError()])
def test_healthcheck_network_failure(error, monkeypatch):
    monkeypatch.setattr(healthcheck.requests, 'get', MagicMock(side_effect=error))
    assert healthcheck.healthy() is False


def test_healthcheck_invalid_json(monkeypatch):
    response = MagicMock(status_code=200)
    response.json.side_effect = ValueError('invalid JSON')
    monkeypatch.setattr(healthcheck.requests, 'get', MagicMock(return_value=response))
    assert healthcheck.healthy() is False
    response.close.assert_called_once()


def test_backend_binding_and_worker_lifecycle():
    config = runpy.run_path(str(ROOT / 'gunicorn.conf.py'))
    assert config['bind'] == '127.0.0.1:8081'
    assert config['workers'] == 1
    assert config['preload_app'] is False


def test_production_start_requires_admin_token():
    env = dict(os.environ, NBTI_ADMIN_TOKEN='')
    result = subprocess.run(['bash', str(ROOT / 'start.sh')], env=env, capture_output=True, timeout=5)
    assert result.returncode == 1
    assert b'NBTI_ADMIN_TOKEN' in result.stderr


def _wait_for(path, process):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if path.exists():
            return
        if process.poll() is not None:
            break
        time.sleep(0.02)
    raise AssertionError(f'Timed out waiting for {path.name}')


@pytest.mark.parametrize('mode', ['child-failure', 'terminate'])
def test_supervisor_stops_other_processes(tmp_path, mode):
    executable = tmp_path / 'gunicorn'
    executable.write_text(f'#!{sys.executable}\n' + '''
import os, signal, sys, time
from pathlib import Path
state = Path(os.environ['FAKE_STATE'])
role = 'backend' if sys.argv[-1] == 'server:app' else 'frontend'
def stop(*args):
    (state / (role + '.stopped')).touch()
    raise SystemExit(0)
signal.signal(signal.SIGTERM, stop)
(state / (role + '.started')).touch()
if role == 'backend' and os.environ['FAKE_MODE'] == 'child-failure':
    for _ in range(200):
        if (state / 'frontend.started').exists():
            raise SystemExit(7)
        time.sleep(0.01)
while True:
    time.sleep(0.05)
''')
    executable.chmod(0o755)
    env = dict(os.environ, PATH=str(tmp_path) + os.pathsep + os.environ['PATH'],
               NBTI_ADMIN_TOKEN='test-token', FAKE_STATE=str(tmp_path), FAKE_MODE=mode)
    process = subprocess.Popen(['bash', str(ROOT / 'start.sh')], env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        if mode == 'terminate':
            _wait_for(tmp_path / 'backend.started', process)
            _wait_for(tmp_path / 'frontend.started', process)
            process.send_signal(signal.SIGTERM)
        assert process.wait(timeout=10) == (7 if mode == 'child-failure' else 143)
        assert (tmp_path / 'frontend.stopped').exists()
        if mode == 'terminate':
            assert (tmp_path / 'backend.stopped').exists()
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
