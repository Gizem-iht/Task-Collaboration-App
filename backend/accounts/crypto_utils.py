import os, json, base64
from django.conf import settings
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def _get_key() -> bytes:
    key_b64 = getattr(settings, "ENCRYPTION_KEY_B64", "")
    if not key_b64:
        raise RuntimeError("ENCRYPTION_KEY_B64 not set")
    key = base64.b64decode(key_b64)
    if len(key) != 32:
        raise RuntimeError("ENCRYPTION_KEY_B64 must decode to 32 bytes")
    return key

def encrypt_json(payload: dict) -> dict:
    iv = os.urandom(12)
    plaintext = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    aesgcm = AESGCM(_get_key())
    ct = aesgcm.encrypt(iv, plaintext, None)
    return {
        "encrypted": True,
        "payload": {
            "iv": base64.b64encode(iv).decode(),
            "data": base64.b64encode(ct).decode(),
        }
    }
