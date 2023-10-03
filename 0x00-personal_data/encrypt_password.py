#!/usr/bin/env python3
""" Password-based encryption
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """ Encrypts a password

    Args:
        password (str): Password to encrypt

    Returns:
        bytes: Salted, hashed password, which is a byte string.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


def is_valid(hash_password: bytes, password: str) -> bool:
    """ Checks if a password is valid

    Args:
        hash_password (bytes): Hashed password
        password (str): Password to check

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    except Exception:
        return False
