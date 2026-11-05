"""Configuration precedence, independent defaults, and atomic save regressions."""

import copy
import json
from concurrent.futures import ThreadPoolExecutor

import pytest

import nbti.config as config


@pytest.fixture
def config_path(tmp_path, monkeypatch):
    path = tmp_path / 'config.json'
    monkeypatch.setattr(config, 'CONFIG_FILE', str(path))
    return path


def test_environment_overrides_saved_key(config_path, monkeypatch):
    config_path.write_text(json.dumps({'llm_profiles': [{
        'name': 'LongCat', 'vendor': 'longcat', 'api_key': 'saved-placeholder',
    }]}))
    monkeypatch.setenv('NBTI_API_KEY_LONGCAT', 'environment-test-value')
    assert config.load_config()['llm_profiles'][0]['api_key'] == 'environment-test-value'
    assert json.loads(config_path.read_text())['llm_profiles'][0]['api_key'] == 'saved-placeholder'


@pytest.mark.parametrize(('name', 'vendor', 'variable'), [
    ('Doubao Mini', 'doubao', 'NBTI_API_KEY_DOUBAO'),
    ('LongCat Flash', 'longcat', 'NBTI_API_KEY_LONGCAT'),
    ('LM Studio Local', 'lmstudio', 'NBTI_API_KEY_LM_STUDIO'),
    ('Custom DeepSeek', 'deepseek', 'NBTI_API_KEY_DEEPSEEK'),
])
def test_vendor_environment_fallback(name, vendor, variable, monkeypatch):
    monkeypatch.setenv(variable, 'vendor-test-value')
    assert config.get_api_key(name, 'saved', vendor) == 'vendor-test-value'


def test_profile_environment_takes_priority(monkeypatch):
    monkeypatch.setenv('NBTI_API_KEY_DOUBAO_MINI', 'specific')
    monkeypatch.setenv('NBTI_API_KEY_DOUBAO', 'vendor')
    assert config.get_api_key('Doubao Mini', 'saved', 'doubao') == 'specific'
    monkeypatch.setenv('NBTI_API_KEY_DOUBAO_MINI', '')
    assert config.get_api_key('Doubao Mini', 'saved', 'doubao') == 'vendor'
    monkeypatch.setenv('NBTI_API_KEY_DOUBAO', '')
    assert config.get_api_key('Doubao Mini', 'saved', 'doubao') == 'saved'


def test_missing_config_applies_environment_without_mutating_defaults(config_path, monkeypatch):
    before = copy.deepcopy(config.DEFAULT_CONFIG)
    monkeypatch.setenv('NBTI_API_KEY_LONGCAT', 'temporary-value')
    first = config.load_config()
    assert config.find_profile(first, 'LongCat Flash')['api_key'] == 'temporary-value'
    first['llm_profiles'][0]['name'] = 'changed'
    assert config.DEFAULT_CONFIG == before
    assert config.load_config()['llm_profiles'][0]['name'] == before['llm_profiles'][0]['name']


@pytest.mark.parametrize('content', ['invalid json', '[]', 'null', '{"llm_profiles": [1]}'])
def test_malformed_config_falls_back_safely(config_path, content):
    config_path.write_text(content)
    loaded = config.load_config()
    assert loaded is not config.DEFAULT_CONFIG
    assert loaded['llm_profiles'][0]['name'] == config.DEFAULT_PROFILES[0]['name']


def test_defaults_merged_without_aliasing(config_path):
    config_path.write_text('{"llm_profiles": []}')
    loaded = config.load_config()
    loaded['easter_eggs']['buddha'] = 999
    assert config.DEFAULT_CONFIG['easter_eggs']['buddha'] != 999


def test_concurrent_atomic_writes(config_path):
    values = [{'writer': i, 'payload': 'x' * 1000} for i in range(32)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(config.save_config, values))
    assert json.loads(config_path.read_text()) in values
    assert not list(config_path.parent.glob('.config-*.tmp'))
