from datetime import datetime
import enum
from dataclasses import dataclass, asdict


@dataclass(kw_only=True)
class DomainModel:
    id: int = None

    def asdict(self):
        def convert_value(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, enum.Enum):
                return obj.value.lower()
            elif isinstance(obj, DomainModel):
                return obj.asdict()
            elif isinstance(obj, dict):
                return {k: convert_value(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_value(item) for item in obj]
            elif isinstance(obj, type):
                return str(obj)
            elif hasattr(obj, "__dict__"):
                return {k: convert_value(v) for k, v in obj.__dict__.items()}
            return obj

        result = {}
        for key, value in asdict(self).items():
            result[key] = convert_value(value)
        return result
