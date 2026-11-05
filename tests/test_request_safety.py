"""Input limits, malformed admin payloads, legacy shares and proxy cleanup."""

import json
from unittest.mock import MagicMock

import pytest

import frontend_server
import nbti.app as backend
import nbti.config as config
from nbti.conversation import is_valid_conversation_id
from nbti.limits import MAX_REQUEST_BYTES


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, 'CONFIG_FILE', str(tmp_path / 'config.json'))
    monkeypatch.setattr(backend, 'share_store', backend.ShareStore(str(tmp_path / 'shares')))
    monkeypatch.delenv('NBTI_ADMIN_TOKEN', raising=False)
    app = backend.create_app()
    app.config['TESTING'] = True
    return app.test_client()


@pytest.mark.parametrize('payload', [None, [], 'text', 42, {'llm_profiles': [1]},
    {'llm_profiles': {}}, {'phase_profiles': []}, {'prompt_presets': []},
    {'easter_eggs': 'no'}, {'min_questions': 0}, {'max_questions': 'bad'},
    {'rate_limit_per_minute': -1}, {'rate_limit_per_minute': True},
    {'llm_profiles': [{'api_key': 1}]}, {'llm_profiles': [{'base_url': []}]},
])
def test_bad_configuration_is_rejected_without_writing(client, payload):
    response = client.post('/api/config', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400
    assert not __import__('pathlib').Path(config.CONFIG_FILE).exists()


@pytest.mark.parametrize('payload', [None, [], ['profile'], 'text', 42,
    {'base_url': [], 'api_key': 'test'}, {'base_url': 'http://[', 'api_key': 'test'},
    {'base_url': 'http://localhost:invalid', 'api_key': 'test'},
])
def test_bad_connection_input_is_rejected(client, payload):
    response = client.post('/api/config/test-connection', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400


def test_backend_and_proxy_reject_oversize_requests(client, monkeypatch):
    body = b'x' * (MAX_REQUEST_BYTES + 1)
    assert client.post('/api/chat', data=body, content_type='application/json').status_code == 413
    proxy_request = MagicMock()
    monkeypatch.setattr(frontend_server.requests, 'request', proxy_request)
    assert frontend_server.app.test_client().post('/api/chat', data=body).status_code == 413
    proxy_request.assert_not_called()


def test_share_infinite_score_is_safe(client):
    response = client.post('/api/share', json={'result': {}, 'scores': {'nb': float('inf')}})
    assert response.status_code == 200
    snapshot = client.get('/api/share/' + response.json['id']).json
    assert snapshot['scores']['nb'] == 0


def test_legacy_eight_character_share_still_works(client):
    backend.share_store.save_snapshot('abcd1234', {'result': {}, 'created_at': 123})
    assert client.get('/api/share/abcd1234').status_code == 200


def test_ids_must_not_have_trailing_newlines():
    assert not is_valid_conversation_id('abc\n')
    assert frontend_server.app.test_client().get('/share/abc%0A').status_code == 404


@pytest.mark.parametrize('streaming', [False, True])
def test_proxy_filters_hop_headers_and_closes_upstream(monkeypatch, streaming):
    response = MagicMock(status_code=200)
    response.headers = {'content-type': 'text/event-stream' if streaming else 'application/json',
                        'Connection': 'X-Upstream-Hop'}
    response.raw.headers = dict(response.headers, **{'X-Upstream-Hop': 'remove', 'X-End-To-End': 'keep'})
    response.content = b'{"ok": true}'
    response.iter_content.return_value = iter([b'data: 1\n\n', b'data: 2\n\n'])
    send = MagicMock(return_value=response)
    monkeypatch.setattr(frontend_server.requests, 'request', send)
    result = frontend_server.app.test_client().post('/api/example', data=b'body', buffered=False,
        headers={'Connection': 'X-Client-Hop', 'X-Client-Hop': 'remove', 'X-Admin-Token': 'keep',
                 'X-Forwarded-For': 'spoofed'})
    assert result.status_code == 200
    result.close()
    forwarded = {k.lower(): v for k, v in send.call_args.kwargs['headers'].items()}
    assert 'x-client-hop' not in forwarded
    assert 'connection' not in forwarded
    assert 'content-length' not in forwarded
    assert forwarded['x-admin-token'] == 'keep'
    assert forwarded['x-forwarded-for'] == '127.0.0.1'
    assert 'X-Upstream-Hop' not in result.headers
    assert result.headers['X-End-To-End'] == 'keep'
    assert response.close.called
