from services.password_service import hash_password, verify_password


class TestPasswordService:
    """Test password hashing and verification"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "TestPass123!"
        hashed = hash_password(password)

        # Hash should be different from original password
        assert hashed != password

        # Hash should be a string and have reasonable length
        # (bcrypt hashes are ~60 chars)
        assert isinstance(hashed, str)
        assert len(hashed) >= 50  # bcrypt hashes are typically 59-60 chars

        # Hash should start with bcrypt identifier
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "TestPass123!"
        hashed = hash_password(password)

        # Correct password should verify
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "TestPass123!"
        wrong_password = "WrongPass456!"
        hashed = hash_password(password)

        # Wrong password should not verify
        assert verify_password(wrong_password, hashed) is False

    def test_hash_same_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)"""
        password = "TestPass123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Same password should produce different hashes due to random salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_hash_different_passwords(self):
        """Test that different passwords produce different hashes"""
        password1 = "TestPass123!"
        password2 = "DifferentPass456!"

        hash1 = hash_password(password1)
        hash2 = hash_password(password2)

        # Different passwords should produce different hashes
        assert hash1 != hash2

        # Each should only verify with its own password
        assert verify_password(password1, hash1) is True
        assert verify_password(password2, hash2) is True
        assert verify_password(password1, hash2) is False
        assert verify_password(password2, hash1) is False
