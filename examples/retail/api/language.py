"""Retail catalog language views over one set of business identifiers and amounts."""

from __future__ import annotations

import json
import re
from contextvars import ContextVar
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

language: ContextVar[str] = ContextVar("retail_language", default="en")
Record = TypeVar("Record", bound=BaseModel)


def search_tokens(query: str) -> list[str]:
    parts = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]+", query.lower())
    result = list(parts)
    for part in parts:
        if re.search(r"[\u4e00-\u9fff]", part):
            result.extend(part[i : i + 2] for i in range(len(part) - 1))
    return list(dict.fromkeys(result))


class CatalogLanguage:
    def __init__(self, data_dir: Path) -> None:
        catalog = json.loads((data_dir / "catalog.json").read_text())
        self.source_language = catalog.get("source_language", "en")
        if self.source_language not in {"en", "zh"}:
            raise ValueError("catalog.json: source_language must be en or zh")
        path = data_dir / "translations.json"
        self.products = json.loads(path.read_text()) if path.exists() else {}
        policies = data_dir / "policy-translations.json"
        self.policies = json.loads(policies.read_text()) if policies.exists() else {}

    def record(self, value: Record) -> Record:
        """Project translated content without modifying the canonical object."""
        if language.get() == self.source_language:
            return value
        return type(value).model_validate(self.payload(value.model_dump()))

    def payload(self, value: Any) -> Any:
        if language.get() == self.source_language:
            return value
        if isinstance(value, list):
            return [self.payload(item) for item in value]
        if not isinstance(value, dict):
            return value
        result = {key: self.payload(item) for key, item in value.items()}
        product_id = value.get("product_id")
        fields = self.products.get(language.get(), {}).get(product_id, {})
        if value.get("policy_id"):
            fields = self.policies.get(language.get(), {}).get(value["policy_id"], {})
        # Only content already present in the response is projected. Cart lines do
        # not acquire detail fields, and identifiers, amounts and currency never change.
        for key, translated in fields.items():
            if key in result and key != "aliases":
                if isinstance(translated, dict) and isinstance(result[key], dict):
                    result[key] = {**result[key], **translated}
                else:
                    result[key] = translated
        return result

    def search_texts(self, product_id: str) -> list[str]:
        texts = []
        for products in self.products.values():
            fields = products.get(product_id, {})
            texts.append(json.dumps(fields, ensure_ascii=False).lower())
        return texts

    def chinese_terms(self, product_id: str, query_tokens: list[str]) -> int:
        fields = self.products.get("zh", {}).get(product_id, {})
        aliases = fields.get("aliases", [])
        query = " ".join(query_tokens)
        # CJK words are not whitespace-delimited. Prepared aliases provide bounded
        # terms instead of matching a single common character in every description.
        return sum(
            1
            for alias in aliases
            if len(alias) >= 2 and re.search(r"[\u4e00-\u9fff]", alias) and alias in query
        )
