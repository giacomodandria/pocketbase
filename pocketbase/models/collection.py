from __future__ import annotations

from dataclasses import fields as dataclass_fields
from typing import Any

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.models.utils.collection_field import CollectionField


class Collection(BaseModel):
    name: str
    type: str
    fields: list[CollectionField]
    system: bool
    list_rule: str | None
    view_rule: str | None
    create_rule: str | None
    update_rule: str | None
    delete_rule: str | None
    options: dict[str, Any]

    @staticmethod
    def _normalize_field(field: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(field)
        normalized["auto_generate_pattern"] = normalized.pop(
            "autogeneratePattern", None
        )
        normalized["primary_key"] = normalized.pop("primaryKey", False)
        allowed_keys = {f.name for f in dataclass_fields(CollectionField)}
        options = dict(normalized.pop("options", {}) or {})
        for key in list(normalized.keys()):
            if key not in allowed_keys:
                options[key] = normalized.pop(key)
        normalized["options"] = options
        return normalized

    def load(self, data: dict[str, Any]) -> None:
        super().load(data)
        self.name = data.get("name", "")
        self.system = data.get("system", False)
        self.type = data.get("type", "base")
        self.options = data.get("options", {})

        # rules
        self.list_rule = data.get("listRule", None)
        self.view_rule = data.get("viewRule", None)
        self.create_rule = data.get("createRule", None)
        self.update_rule = data.get("updateRule", None)
        self.delete_rule = data.get("deleteRule", "")

        # fields
        fields = data.get("fields", [])
        self.fields = []
        for field in fields:
            self.fields.append(
                CollectionField(**self._normalize_field(field))
            )

    def is_base(self):
        return self.type == "base"

    def is_auth(self):
        return self.type == "auth"

    def is_single(self):
        return self.type == "single"
