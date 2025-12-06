"""
Unit tests for authentication utilities

Tests password hashing, JWT token creation/validation in isolation.
No external dependencies required - fast execution.
Following cheese-app-ci-cd reference pattern.
"""

import pytest
from datetime import timedelta

from utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


class TestPasswordHashing:
    """Tests for password hashing functions"""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string"""
        hashed = hash_password("testpassword")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_not_plaintext(self):
        """Test that hashed password is not the same as plaintext"""
        password = "testpassword123"
        hashed = hash_password(password)
        assert hashed != password

    def test_hash_password_unique_salts(self):
        """Test that same password produces different hashes (unique salts)"""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "mysecurepassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "mysecurepassword"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_empty(self):
        """Test password verification with empty password"""
        hashed = hash_password("somepassword")
        assert verify_password("", hashed) is False

    def test_hash_long_password(self):
        """Test hashing of long password (bcrypt 72-byte limit)"""
        # Passwords longer than 72 bytes should still work
        long_password = "a" * 100
        hashed = hash_password(long_password)
        assert verify_password(long_password, hashed) is True

    def test_hash_special_characters(self):
        """Test hashing password with special characters"""
        password = "p@$$w0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Tests for JWT token creation and validation"""

    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a string"""
        token = create_access_token({"username": "testuser"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_data(self):
        """Test token contains encoded data"""
        data = {"username": "testuser", "role": "admin"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        assert decoded["username"] == "testuser"
        assert decoded["role"] == "admin"

    def test_decode_access_token_contains_exp(self):
        """Test decoded token contains expiration"""
        token = create_access_token({"username": "testuser"})
        decoded = decode_access_token(token)
        assert "exp" in decoded
        assert "iat" in decoded

    def test_create_access_token_custom_expiry(self):
        """Test token with custom expiration"""
        data = {"username": "testuser"}
        token = create_access_token(data, expires_delta=timedelta(hours=1))
        decoded = decode_access_token(token)
        assert decoded["username"] == "testuser"

    def test_decode_invalid_token(self):
        """Test decoding invalid token raises exception"""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401

    def test_token_preserves_complex_data(self):
        """Test token preserves nested data structures"""
        data = {
            "username": "testuser",
            "role": "nurse",
            "department": "internal medicine",
            "email": "test@hospital.com"
        }
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        assert decoded["username"] == data["username"]
        assert decoded["role"] == data["role"]
        assert decoded["department"] == data["department"]
        assert decoded["email"] == data["email"]
