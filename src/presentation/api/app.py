from typing import Dict, Any

from fastapi import FastAPI

from src.infrastructure.container import Container


class Application(FastAPI):
    def __init__(self, *args, container: Container = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.container = container

    def openapi(self) -> Dict[str, Any]:  # This removes default 422 responses
        result = super().openapi()
        for path in result["paths"].values():
            for method in path.values():
                responses = method.get("responses")
                if "422" in responses:
                    del responses["422"]
        return result
