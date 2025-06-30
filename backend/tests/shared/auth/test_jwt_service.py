import pytest
from app.shared.auth.jwt_service import create_access_token, decode_access_token

def test_create_and_decode_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded["sub"] == "testuser"