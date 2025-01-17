from pathlib import Path

from tomllib import loads

__all__ = ["nameless_config"]

_cfg_path: Path = Path.cwd() / "nameless.toml"
_content: str = ""

with open(_cfg_path, encoding="utf-8") as f:
    _content = f.read()

nameless_config = loads(_content)
