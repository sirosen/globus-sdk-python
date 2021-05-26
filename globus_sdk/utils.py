import hashlib
from base64 import b64encode


def sha256_string(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def safe_b64encode(s):
    try:
        encoded = b64encode(s.encode("utf-8"))
    except UnicodeDecodeError:
        encoded = b64encode(s)

    return encoded.decode("utf-8")


def slash_join(a, b):
    """
    Join a and b with a single slash, regardless of whether they already
    contain a trailing/leading slash or neither.
    """
    if not b:  # "" or None, don't append a slash
        return a
    if a.endswith("/"):
        if b.startswith("/"):
            return a[:-1] + b
        return a + b
    if b.startswith("/"):
        return a + b
    return a + "/" + b


def safe_stringify(value):
    """
    Converts incoming value to a unicode string. Convert bytes by decoding,
    anything else has __str__ called.
    Strings are checked to avoid duplications
    """
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)
