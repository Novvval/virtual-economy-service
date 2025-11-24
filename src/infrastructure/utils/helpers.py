from enum import Enum
from jwt import encode
import hashlib


def generate_jwt(data: dict, secret_key: str) -> str:
    return encode(data, secret_key, algorithm="HS256")


def generate_hash(string: str) -> str:
    return hashlib.sha256(string.encode("utf-8")).hexdigest()


def cast_dict_types(data: dict | list[dict]) -> dict | list[dict]:
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value.lower()
    elif isinstance(data, list):
        for item in data:
            cast_dict_types(item)
    return data
