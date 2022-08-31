from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._config import Config

REX_LINE = re.compile(r"""
    (?P<path>.+\.py):
    (?P<lineno>[0-9]+):\s
    (?P<severity>[a-z]+):\s
    (?P<message>.+)\s\s
    \[(?P<category>[a-z-]+)\]
""", re.VERBOSE)


@dataclass
class Error:
    raw_line: str
    _match: re.Match

    @classmethod
    def new(self, line: str) -> Error | None:
        match = REX_LINE.fullmatch(line)
        if match is None:
            return None
        return Error(line, match)

    @cached_property
    def path(self) -> Path:
        return Path(self._match.group('path'))

    @cached_property
    def line_number(self) -> int:
        result = int(self._match.group('lineno'))
        assert result >= 0
        return result

    @cached_property
    def severity(self) -> str:
        return self._match.group('severity')

    @cached_property
    def message(self) -> str:
        return self._match.group('message')

    @cached_property
    def category(self) -> str:
        return self._match.group('category')

    def get_clean_line(self, config: Config) -> str:
        path = Path(*self.path.parts[:config.depth])
        pos = self.line_number if config.preserve_position else 0
        return f'{path}:{pos}: {self.severity}: {self.message}  [{self.category}]'