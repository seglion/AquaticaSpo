import pytest
from app.shared.auth.jwt_service import JWTService

def test_create_and_decode_access_token():
    service = JWTService(secret_key="testsecret")
    subject = "testuser"
    token = service.create_access_token(subject=subject)
    
    assert isinstance(token, str)
    
    decoded = service.decode_token(token)
    assert decoded["sub"] == subject