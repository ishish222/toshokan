from __future__ import annotations

import json
from importlib import resources

from ..domain import GrammarTarget

_DEFAULT_TARGETS: list[GrammarTarget] | None = None


def load_default_grammar_targets() -> list[GrammarTarget]:
    with resources.files(__package__).joinpath(
        "default_grammar_targets.json"
    ).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    return [
        GrammarTarget(
            id=str(item.get("id", "")),
            label=str(item.get("label", "")),
            description=item.get("description"),
        )
        for item in payload
    ]


def set_default_grammar_targets(targets: list[GrammarTarget]) -> None:
    global _DEFAULT_TARGETS
    _DEFAULT_TARGETS = list(targets)


def get_default_grammar_targets() -> list[GrammarTarget]:
    if _DEFAULT_TARGETS is None:
        return load_default_grammar_targets()
    return list(_DEFAULT_TARGETS)
