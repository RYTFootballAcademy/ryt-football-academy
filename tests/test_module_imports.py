"""Import every application module so hidden dependency/import errors fail CI."""

from __future__ import annotations

import importlib
import pkgutil

import ai_agent.core
import ai_agent.crm
import ai_agent.faos
import ai_agent.modules


PACKAGES = [
    ai_agent.core,
    ai_agent.crm,
    ai_agent.faos,
    ai_agent.modules,
]


def test_all_application_modules_import():
    failures: list[str] = []
    for package in PACKAGES:
        for module_info in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            try:
                importlib.import_module(module_info.name)
            except Exception as exc:  # pragma: no cover - failure detail is the point of this smoke test
                failures.append(f"{module_info.name}: {type(exc).__name__}: {exc}")

    assert not failures, "Module import failures:\n" + "\n".join(failures)
