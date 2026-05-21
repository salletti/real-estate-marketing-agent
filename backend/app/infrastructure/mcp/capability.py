from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    name: str
    description: str
    input_schema: dict
    server_name: str
    server_url: str
