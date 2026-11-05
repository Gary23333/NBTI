"""The public frontend must never serve private repository data as static files."""

import pytest

import frontend_server


@pytest.fixture
def frontend(tmp_path, monkeypatch):
    monkeypatch.setattr(frontend_server, "STATIC_DIR", str(tmp_path))
    monkeypatch.setitem(frontend_server.app.config, "TESTING", True)
    return frontend_server.app.test_client(), tmp_path


@pytest.mark.parametrize("filename", [
    "data/config.json",
    "data/conversations/demo.json",
    "data/shares/demo.json",
    "logs/debug.json",
    ".git/config.json",
    "config.json",
    "secrets.json",
    "data/leak.html",
    "data/leak.js",
    "tests/fixture.json",
])
def test_private_files_are_not_public(frontend, filename):
    client, root = frontend
    target = root / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("private-test-marker", encoding="utf-8")
    response = client.get("/" + filename)
    assert response.status_code == 404
    assert b"private-test-marker" not in response.data


@pytest.mark.parametrize("url", ["/data%2Fconfig.json", "/%64ata/config.json"])
def test_encoded_private_paths_are_not_public(frontend, url):
    client, root = frontend
    (root / "data").mkdir()
    (root / "data/config.json").write_text("private-test-marker", encoding="utf-8")
    response = client.get(url)
    assert response.status_code == 404
    assert b"private-test-marker" not in response.data


@pytest.mark.parametrize("filename", [
    "index.html", "config.html", "share.html", "app.js",
    "avatar-generator.js", "compat-data.js", "radar-chart.js",
    "share-poster.js", "sw.js", "style.css", "config.css",
    "icon.svg", "manifest.json",
])
def test_public_assets_remain_accessible(frontend, filename):
    client, root = frontend
    (root / filename).write_text("public-test-marker", encoding="utf-8")
    response = client.get("/" + filename)
    assert response.status_code == 200
    assert response.data == b"public-test-marker"


def test_page_routes_remain_accessible(frontend):
    client, root = frontend
    (root / "index.html").write_text("home", encoding="utf-8")
    (root / "share.html").write_text("share", encoding="utf-8")
    assert client.get("/").data == b"home"
    assert client.get("/share/demo_123").data == b"share"
    assert client.get("/share/invalid.id").status_code == 404
