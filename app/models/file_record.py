from dataclasses import dataclass, field


@dataclass
class FileRecord:
    id: str
    filename: str
    feature_count: int
    crs: str | None
    status: str
    measurements: list[dict] = field(default_factory=list)