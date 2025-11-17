"""
Authentication Module
=====================

JWT-based authentication for the Credit Risk API.

Features:
- User authentication with JWT tokens
- Password hashing with bcrypt
- Token expiration
- Dependency injection for protected routes

In Production:
- Use a real database for user storage
- Implement role-based access control (RBAC)
- Add refresh tokens
- Implement rate limiting
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from src.api.schemas import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fake database of users (in production, use real database)
# Password is "password123" for all demo users
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "System Administrator",
        "email": "admin@creditrisk.ng",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password123
        "disabled": False,
    },
    "loan_officer": {
        "username": "loan_officer",
        "full_name": "John Doe",
        "email": "john.doe@bank.ng",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password123
        "disabled": False,
    },
    "analyst": {
        "username": "analyst",
        "full_name": "Jane Smith",
        "email": "jane.smith@bank.ng",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password123
        "disabled": False,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[dict]:
    """
    Get user from database.

    Args:
        username: Username to lookup

    Returns:
        User dict if found, None otherwise
    """
    if username in fake_users_db:
        return fake_users_db[username]
    return None


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Authenticate a user.

    Args:
        username: Username
        password: Password

    Returns:
        User dict if authenticated, None otherwise
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get current user from JWT token.

    Args:
        token: JWT token

    Returns:
        User object

    Raises:
        HTTPException if token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception

    return User(**user)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user (not disabled).

    Args:
        current_user: Current user from token

    Returns:
        Active user object

    Raises:
        HTTPException if user is disabled
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Helper function to create initial admin user
def create_admin_user(username: str, password: str, email: str, full_name: str):
    """
    Create a new admin user.

    Args:
        username: Username
        password: Plain text password
        email: Email address
        full_name: Full name
    """
    hashed_password = get_password_hash(password)
    fake_users_db[username] = {
        "username": username,
        "full_name": full_name,
        "email": email,
        "hashed_password": hashed_password,
        "disabled": False,
    }
    print(f"✓ Created user: {username}")


if __name__ == "__main__":
    # Demo: Create a password hash
    print("\n" + "="*70)
    print(" "*25 + "AUTH MODULE DEMO")
    print("="*70)

    password = "password123"
    hashed = get_password_hash(password)
    print(f"\nOriginal password: {password}")
    print(f"Hashed password: {hashed}")

    # Verify
    is_valid = verify_password(password, hashed)
    print(f"Verification: {is_valid}")

    # Create token
    token = create_access_token(data={"sub": "demo_user"})
    print(f"\nJWT Token: {token[:50]}...")

    print("\n" + "="*70)
    print("\nDemo Users (all passwords: 'password123'):")
    print("-" * 70)
    for username, user in fake_users_db.items():
        print(f"  Username: {username:15s} | Name: {user['full_name']}")
    print("="*70 + "\n")
