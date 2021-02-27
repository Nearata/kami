from jwt import decode
from jwt import encode

from kami.config import JWT_SECRET, JWT_ALGORITHM


def jwt_decode(jwt: str) -> dict:
    return decode(jwt, str(JWT_SECRET), algorithms=[JWT_ALGORITHM])

def jwt_encode(payload: dict) -> bytes:
    return encode(payload, str(JWT_SECRET), algorithm=JWT_ALGORITHM)
