from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError, ExpiredSignatureError

class JWTService:
    def __init__(self, secret_key: str, algorithm: str = "HS256", access_token_expire_minutes: int = 30):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    def create_access_token(self, subject: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "sub": subject,
            "iat": now,
            "exp": expire
        }
        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except ExpiredSignatureError as e:
            raise ExpiredSignatureError("Token has expired") from e
        except JWTError as e:
            raise JWTError("Invalid token") from e

    def verify_token(self, token: str, subject: Optional[str] = None) -> bool:
        payload = self.decode_token(token)
        if subject and payload.get("sub") != subject:
            raise JWTError("Token subject mismatch")
        return True