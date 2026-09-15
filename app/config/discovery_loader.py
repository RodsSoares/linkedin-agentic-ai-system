import json
from pathlib import Path

from pydantic import ValidationError

from app.schemas.discovery_config import DiscoveryConfig


DEFAULT_DISCOVERY_CONFIG_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "discovery.json"
)


class DiscoveryConfigError(RuntimeError):
    """Raised when discovery configuration cannot be loaded."""


def load_discovery_config(
    path: str | Path | None = None,
) -> DiscoveryConfig:
    config_path = (
        Path(path)
        if path is not None
        else DEFAULT_DISCOVERY_CONFIG_PATH
    )

    if not config_path.exists():
        raise DiscoveryConfigError(
            f"Discovery configuration file not found: {config_path}"
        )

    if not config_path.is_file():
        raise DiscoveryConfigError(
            f"Discovery configuration path is not a file: {config_path}"
        )

    try:
        raw_content = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DiscoveryConfigError(
            f"Could not read discovery configuration: {config_path}"
        ) from exc

    try:
        raw_config = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise DiscoveryConfigError(
            f"Invalid JSON in discovery configuration: {config_path}"
        ) from exc

    try:
        return DiscoveryConfig.model_validate(raw_config)
    except ValidationError as exc:
        raise DiscoveryConfigError(
            f"Invalid discovery configuration: {config_path}"
        ) from exc
    