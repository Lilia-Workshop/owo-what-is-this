from pathlib import Path

from tomllib import loads

__all__ = ["nameless_config"]

_cfg_path: Path = Path(__file__).parent.parent.absolute() / "nameless.toml"

with open(_cfg_path, encoding="utf-8") as f:
    _content: str = f.read()

nameless_config = loads(_content)
