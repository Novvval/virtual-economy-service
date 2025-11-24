from abc import ABC

from .db_adapter import DbAdapter


class Repository(ABC):
    def __init__(self, db: DbAdapter):
        self.db = db
