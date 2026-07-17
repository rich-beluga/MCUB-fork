# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Шмэлькa | @hairpin01

import hashlib
import os

import pytest

from utils.security import session_exists

API_ID = 123456
API_HASH = "test-api-hash"


def _expected_mcub_dir(home, api_id=API_ID, api_hash=API_HASH):
    instance_hash = hashlib.sha256(f"{api_id}{api_hash}".encode()).hexdigest()[:16]
    return home / ".MCUB" / instance_hash


def test_session_exists_does_not_create_hash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    assert session_exists(API_ID, API_HASH) is False

    assert not _expected_mcub_dir(tmp_path).exists()
    assert not (tmp_path / ".MCUB").exists()


def test_session_exists_detects_hashed_session_without_creating_more(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    session_file = _expected_mcub_dir(tmp_path) / "sessions" / "user_session.session"
    session_file.parent.mkdir(parents=True)
    session_file.write_bytes(b"")

    assert session_exists(API_ID, API_HASH) is True
    assert sorted(p.name for p in _expected_mcub_dir(tmp_path).iterdir()) == [
        "sessions"
    ]


def test_session_exists_legacy_cwd_session_stays_read_only(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "user_session.session").write_bytes(b"")

    assert session_exists(API_ID, API_HASH) is True
    assert not _expected_mcub_dir(tmp_path).exists()


def test_session_exists_refuses_symlinked_hash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "target"
    target.mkdir()
    mcub_dir = _expected_mcub_dir(tmp_path)
    mcub_dir.parent.mkdir()
    os.symlink(target, mcub_dir)

    with pytest.raises(PermissionError, match="is a symlink"):
        session_exists(API_ID, API_HASH)
