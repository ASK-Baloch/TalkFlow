from __future__ import annotations

import importlib
from typing import Any


def load_class(class_path: str) -> type[Any]:
    """
    Load:

        package.module:ClassName

    without business code importing the concrete implementation.
    """

    if ":" not in class_path:
        raise ValueError(
            "Provider class path must use "
            "'module.path:ClassName' format"
        )

    module_name, class_name = class_path.split(
        ":",
        1,
    )

    module = importlib.import_module(
        module_name
    )

    provider_class = getattr(
        module,
        class_name,
        None,
    )

    if provider_class is None:
        raise ImportError(
            f"Provider class '{class_name}' "
            f"does not exist in '{module_name}'"
        )

    if not isinstance(
        provider_class,
        type,
    ):
        raise TypeError(
            f"{class_path} is not a class"
        )

    return provider_class


def create_provider(
    class_path: str,
    *,
    settings: Any,
) -> Any:
    provider_class = load_class(
        class_path
    )

    factory = getattr(
        provider_class,
        "from_settings",
        None,
    )

    if factory is None:
        raise TypeError(
            f"{class_path} must implement "
            "from_settings(settings)"
        )

    return factory(
        settings
    )