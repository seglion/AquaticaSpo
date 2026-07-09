class JWTError(Exception):
    pass

class JWTExpiredError(JWTError):
    pass

class JWTInvalidError(JWTError):
    pass