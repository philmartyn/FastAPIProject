"""Tests for password hashing and verification."""

from app.security import hash_password, verify_password


def test_hash_is_not_plaintext():
    hashed = hash_password("s3cret")
    assert hashed != "s3cret"
    # bcrypt hashes start with a version/cost marker like "$2b$".
    assert hashed.startswith("$2")


def test_hash_is_salted():
    assert hash_password("s3cret") != hash_password("s3cret")


def test_verify_accepts_correct_password():
    hashed = hash_password("s3cret")
    assert verify_password("s3cret", hashed) is True


def test_verify_rejects_wrong_password():
    hashed = hash_password("s3cret")
    assert verify_password("not-it", hashed) is False
