"""Policy compiler for machine-readable Helix rules."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional

from .core import Interaction


class PolicyCompiler:
    """
    Transform human-readable rule documents into executable checks.
    """

    def __init__(self, rule_source: Optional[str] = None):
        self.rules: Dict[str, Any] = {}
        if rule_source:
            with open(rule_source, "r", encoding="utf-8") as f:
                self.rules = json.load(f)
        self.executable_checks: List[Callable[[Interaction], bool]] = []
        self._compile()

    def _compile(self) -> None:
        self.executable_checks = []

        if self.rules.get("jurisdiction") == "ITAR":
            self.executable_checks.append(
                lambda i: i.authority in {"CUSTODIAN_ITAR", "SYSADMIN"}
            )

        max_velocity = self.rules.get("constraints", {}).get("max_velocity")
        if max_velocity == "PAUSE":
            self.executable_checks.append(lambda i: i.velocity != "PROCEED")

        if self.rules.get("mode") == "STRICT_FACT":
            self.executable_checks.append(lambda i: i.form == "FACT")

        trigger = self.rules.get("trigger", {})
        action = self.rules.get("action", {})
        trigger_form = trigger.get("form_en")
        trigger_classes = (
            trigger.get("context", {}).get("data_classification", {}).get("enum", [])
        )
        required_velocity = action.get("velocity_en")
        required_authority = action.get("authority_en")

        if trigger_form or trigger_classes or required_velocity or required_authority:
            self.executable_checks.append(
                lambda i: self._validate_triggered_rule(
                    i,
                    trigger_form=trigger_form,
                    trigger_classes=trigger_classes,
                    required_velocity=required_velocity,
                    required_authority=required_authority,
                )
            )

    @staticmethod
    def _validate_triggered_rule(
        interaction: Interaction,
        *,
        trigger_form: Optional[str],
        trigger_classes: List[str],
        required_velocity: Optional[str],
        required_authority: Optional[str],
    ) -> bool:
        context = interaction.context or {}
        data_classification = context.get("data_classification")

        trigger_matches = True
        if trigger_form:
            trigger_matches = trigger_matches and interaction.form == trigger_form
        if trigger_classes:
            trigger_matches = trigger_matches and data_classification in trigger_classes

        if not trigger_matches:
            return True

        if required_velocity and interaction.velocity != required_velocity:
            return False
        if required_authority and interaction.authority != required_authority:
            return False
        return True

    def validate_interaction(self, interaction: Interaction) -> bool:
        if not self.executable_checks:
            return False
        return all(check(interaction) for check in self.executable_checks)
