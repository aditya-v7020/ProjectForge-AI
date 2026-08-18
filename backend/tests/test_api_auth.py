"""ProjectForge AI — Auth API Endpoint Tests."""
import bcrypt
from backend.app.core.security import hash_password, verify_password
from backend.app.models.user import User


def test_register_user(client):
    """Test user registration endpoint."""
    res = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "secretpassword",
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == "newuser"


def test_login_user(client, test_user):
    """Test user login endpoint."""
    res = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "password123",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data


def test_login_invalid_password(client, test_user):
    """Test login with wrong password."""
    res = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword",
    })
    assert res.status_code == 401


def test_get_me(client, auth_headers):
    """Test getting current user profile."""
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["username"] == "testuser"


def test_password_verification_utility():
    """Test hash_password and verify_password security helper functions."""
    pwd = "MySuperSecretPassword123!"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False


def test_password_near_and_above_72_byte_boundary(client):
    """Test passwords near and beyond bcrypt's 72-byte boundary (e.g. 70, 72, 75, 100 bytes)."""
    long_passwords = [
        "A" * 70,   # 70 bytes
        "B" * 72,   # Exactly 72 bytes
        "C" * 75,   # 75 bytes (> 72 bytes)
        "D" * 100,  # 100 bytes (> 72 bytes)
    ]

    for idx, pwd in enumerate(long_passwords):
        username = f"longuser_{idx}"
        email = f"longuser_{idx}@example.com"

        # Test registration
        reg_res = client.post("/api/auth/register", json={
            "username": username,
            "email": email,
            "password": pwd,
        })
        assert reg_res.status_code == 201, f"Failed registration for password length {len(pwd)}"

        # Test login with correct password
        login_res = client.post("/api/auth/login", json={
            "username": username,
            "password": pwd,
        })
        assert login_res.status_code == 200, f"Failed login for password length {len(pwd)}"
        assert "access_token" in login_res.json()

        # Test login with wrong password of same length
        wrong_pwd = pwd[:-1] + "X"
        bad_login = client.post("/api/auth/login", json={
            "username": username,
            "password": wrong_pwd,
        })
        assert bad_login.status_code == 401, f"Wrong password check failed for length {len(pwd)}"


def test_password_unicode_characters(client):
    """Test registration and login with passwords containing multibyte Unicode characters."""
    unicode_pwd = "Pässwörd_🔐🚀_Complex_über_1234567890"

    reg_res = client.post("/api/auth/register", json={
        "username": "unicodeuser",
        "email": "unicode@example.com",
        "password": unicode_pwd,
    })
    assert reg_res.status_code == 201

    login_res = client.post("/api/auth/login", json={
        "username": "unicodeuser",
        "password": unicode_pwd,
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    bad_login = client.post("/api/auth/login", json={
        "username": "unicodeuser",
        "password": "Pässwörd_🔐🚀_Wrong_123",
    })
    assert bad_login.status_code == 401


def test_legacy_hash_compatibility(client, db_session):
    """Test compatibility with existing database users created with legacy bcrypt hashes."""
    legacy_pwd = "legacy_password_123"
    # Create legacy hash directly using raw bcrypt (no SHA-256 pre-hashing)
    legacy_hash = bcrypt.hashpw(legacy_pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user = User(
        username="legacyuser",
        email="legacy@example.com",
        password_hash=legacy_hash,
    )
    db_session.add(user)
    db_session.commit()

    # Test verify_password helper directly
    assert verify_password(legacy_pwd, legacy_hash) is True
    assert verify_password("wrong_legacy_pwd", legacy_hash) is False

    # Test login via API endpoint
    login_res = client.post("/api/auth/login", json={
        "username": "legacyuser",
        "password": legacy_pwd,
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


def test_login_with_email_and_case_insensitivity(client):
    """Test registering and logging in with email or username regardless of casing."""
    reg = client.post("/api/auth/register", json={
        "username": "JohnDoe",
        "email": "John.Doe@Example.com",
        "password": "mypassword123",
    })
    assert reg.status_code == 201

    # Login with exact username
    l1 = client.post("/api/auth/login", json={"username": "JohnDoe", "password": "mypassword123"})
    assert l1.status_code == 200

    # Login with lowercased username
    l2 = client.post("/api/auth/login", json={"username": "johndoe", "password": "mypassword123"})
    assert l2.status_code == 200

    # Login with email
    l3 = client.post("/api/auth/login", json={"username": "john.doe@example.com", "password": "mypassword123"})
    assert l3.status_code == 200

    # Login with uppercase email
    l4 = client.post("/api/auth/login", json={"username": "JOHN.DOE@EXAMPLE.COM", "password": "mypassword123"})
    assert l4.status_code == 200


def test_duplicate_registration_validation(client):
    """Test duplicate registration returns 400 with clear message."""
    client.post("/api/auth/register", json={
        "username": "uniqueuser",
        "email": "unique@example.com",
        "password": "password123",
    })

    # Duplicate username
    dup_user = client.post("/api/auth/register", json={
        "username": "UNIQUEUSER",
        "email": "different@example.com",
        "password": "password123",
    })
    assert dup_user.status_code == 400

    # Duplicate email
    dup_email = client.post("/api/auth/register", json={
        "username": "differentuser",
        "email": "UNIQUE@example.com",
        "password": "password123",
    })
    assert dup_email.status_code == 400


