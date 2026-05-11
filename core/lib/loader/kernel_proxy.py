# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Шмэлькa | @hairpin01

from __future__ import annotations

from types import MappingProxyType
from typing import Any

from ..utils.exceptions import CallInsecure

PROTECTED_KERNEL_NAMES = frozenset(
    {
        "loaded_modules",
        "system_modules",
        "command_handlers",
        "bot_command_handlers",
        "command_owners",
        "bot_command_owners",
        "aliases",
        "command_metadata",
        "command_docs",
        "inline_handlers",
        "inline_handlers_owners",
        "callback_handlers",
        "callback_permissions",
        "inline_callback_map",
        "_inline_temp_map",
        "_inline_temp_uuids",
        "_class_module_instances",
        "_loader",
        "loader",
    }
)


PROTECTED_REGISTER_NAMES = frozenset({"kernel", "_kernel"})


def _raise_insecure(name: str, module_name: str) -> None:
    raise CallInsecure(name, module_name)


class ModuleRegisterProxy:
    """Safe register facade for user modules.

    Registration calls still go through the real register object so ownership and
    cleanup stay centralized, but modules cannot use ``register.kernel`` as a
    backdoor to mutable kernel internals.
    """

    _LOCAL_NAMES = frozenset(
        {
            "module_name",
            "is_protected",
            "_deny",
            "__class__",
            "__repr__",
            "__dir__",
        }
    )

    def __init__(self, register: Any, module_name: str) -> None:
        object.__setattr__(self, "_register", register)
        object.__setattr__(self, "_module_name", module_name)

    @property
    def module_name(self) -> str:
        return object.__getattribute__(self, "_module_name")

    def is_protected(self, name: str) -> bool:
        return name in PROTECTED_REGISTER_NAMES or name.startswith("_")

    def _deny(self, name: str) -> None:
        _raise_insecure(name, self.module_name)

    def __getattribute__(self, name: str) -> Any:
        if name == "__dict__":
            _raise_insecure(name, object.__getattribute__(self, "_module_name"))
        if name in object.__getattribute__(self, "_LOCAL_NAMES"):
            return object.__getattribute__(self, name)
        if name in PROTECTED_REGISTER_NAMES or name.startswith("_"):
            _raise_insecure(name, object.__getattribute__(self, "_module_name"))
        return getattr(object.__getattribute__(self, "_register"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        self._deny(name)

    def __delattr__(self, name: str) -> None:
        self._deny(name)

    def __dir__(self) -> list[str]:
        register = object.__getattribute__(self, "_register")
        names = set(dir(register)) - PROTECTED_REGISTER_NAMES
        names = {name for name in names if not name.startswith("_")}
        names.update({"module_name", "is_protected"})
        return sorted(names)

    def __repr__(self) -> str:
        return f"<ModuleRegisterProxy module={self.module_name!r}>"


class ModuleKernelProxy:
    """Safe kernel facade for native user modules.

    The proxy keeps normal userbot capabilities available (client, db, cache,
    config, logging, inline helpers, subprocess imports via normal builtins) but
    raises ``CallInsecure`` for direct access to mutable core registries.
    """

    _LOCAL_NAMES = frozenset(
        {
            "module_name",
            "register",
            "is_protected",
            "lookup_module",
            "get_loaded_module",
            "iter_loaded_module_names",
            "loaded_module_names",
            "loaded_modules_view",
            "system_modules_view",
            "_live_module_configs",
            "remove_inline_callback_tokens",
            "store_inline_callback",
            "allow_inline_callback_user",
            "set_live_module_config",
            "get_live_module_config",
            "_ensure_callback_storage",
            "_get_module_state",
            "_deny",
            "__class__",
            "__repr__",
            "__dir__",
        }
    )

    def __init__(self, kernel: Any, module_name: str) -> None:
        object.__setattr__(self, "_kernel", kernel)
        object.__setattr__(self, "_module_name", module_name)
        object.__setattr__(self, "_register_proxy", None)
        object.__setattr__(self, "_module_state", {})

    @property
    def module_name(self) -> str:
        return object.__getattribute__(self, "_module_name")

    @property
    def register(self) -> ModuleRegisterProxy:
        cached = object.__getattribute__(self, "_register_proxy")
        if cached is None:
            kernel = object.__getattribute__(self, "_kernel")
            cached = ModuleRegisterProxy(kernel.register, self.module_name)
            object.__setattr__(self, "_register_proxy", cached)
        return cached

    def is_protected(self, name: str) -> bool:
        return name in PROTECTED_KERNEL_NAMES or name.startswith("_")

    def _deny(self, name: str) -> None:
        _raise_insecure(name, self.module_name)

    def lookup_module(self, module_name: str, *, all_loaded: bool = False) -> Any:
        """Lookup a module without exposing mutable kernel registries.

        Args:
            module_name: Name, class name, or module ``__name__`` to lookup.
            all_loaded: When true, only return modules already present in the
                fully loaded module maps (``loaded_modules``/``system_modules``).
                This intentionally ignores in-progress class instances.
        """
        needle = str(module_name).lower()
        kernel = object.__getattribute__(self, "_kernel")

        if not all_loaded:
            for name, instance in getattr(
                kernel, "_class_module_instances", {}
            ).items():
                if (
                    str(name).lower() == needle
                    or str(getattr(instance, "name", "")).lower() == needle
                ):
                    return instance

        for collection_name in ("loaded_modules", "system_modules"):
            for name, module in getattr(kernel, collection_name, {}).items():
                instance = getattr(module, "_class_instance", None)
                target = instance or module
                names = {
                    str(name).lower(),
                    str(getattr(target, "name", "")).lower(),
                    str(getattr(module, "__name__", "")).lower(),
                }
                if needle in names:
                    return target

        compat_allmodules = getattr(kernel, "_hikka_compat_allmodules_proxy", None)
        if (
            not all_loaded
            and compat_allmodules is not None
            and hasattr(compat_allmodules, "lookup")
        ):
            return compat_allmodules.lookup(module_name)

        return None

    def get_loaded_module(self, module_name: str, *, all_loaded: bool = False) -> Any:
        return self.lookup_module(module_name, all_loaded=all_loaded)

    def iter_loaded_module_names(self) -> tuple[str, ...]:
        kernel = object.__getattribute__(self, "_kernel")
        names = set(getattr(kernel, "loaded_modules", {}).keys())
        names.update(getattr(kernel, "system_modules", {}).keys())
        return tuple(sorted(str(name) for name in names))

    @property
    def loaded_module_names(self) -> tuple[str, ...]:
        return self.iter_loaded_module_names()

    @property
    def loaded_modules_view(self) -> MappingProxyType:
        kernel = object.__getattribute__(self, "_kernel")
        return MappingProxyType(dict(getattr(kernel, "loaded_modules", {})))

    @property
    def system_modules_view(self) -> MappingProxyType:
        kernel = object.__getattribute__(self, "_kernel")
        return MappingProxyType(dict(getattr(kernel, "system_modules", {})))

    @property
    def _live_module_configs(self) -> MappingProxyType:
        """Read-only compatibility view for modules checking live config.

        Older MCUB/repo modules commonly use
        ``getattr(kernel, "_live_module_configs", {}).get(__name__)``. Keep that
        read path working without exposing the mutable kernel mapping itself.
        Mutations must go through ``set_live_module_config``.
        """
        kernel = object.__getattribute__(self, "_kernel")
        return MappingProxyType(dict(getattr(kernel, "_live_module_configs", {})))

    def _get_module_state(self) -> dict[str, Any]:
        return object.__getattribute__(self, "_module_state")

    def _ensure_callback_storage(self) -> tuple[Any, dict[str, Any]]:
        import threading

        kernel = object.__getattribute__(self, "_kernel")
        lock = getattr(kernel, "_inline_cb_lock", None)
        cb_map = getattr(kernel, "inline_callback_map", None)
        if lock is None:
            lock = threading.Lock()
            kernel._inline_cb_lock = lock
        if cb_map is None:
            cb_map = {}
            kernel.inline_callback_map = cb_map
        return lock, cb_map

    def remove_inline_callback_tokens(
        self, tokens: list[str] | tuple[str, ...]
    ) -> None:
        lock, cb_map = self._ensure_callback_storage()
        with lock:
            for token in tokens:
                cb_map.pop(token, None)

    def store_inline_callback(self, token: str, data: dict[str, Any]) -> None:
        import time

        lock, cb_map = self._ensure_callback_storage()
        with lock:
            now = time.time()
            expired = [
                key
                for key, value in list(cb_map.items())
                if value.get("expires_at") and value["expires_at"] < now
            ]
            for key in expired:
                cb_map.pop(key, None)
            cb_map[token] = data

    def allow_inline_callback_user(
        self, user_id: int, token: str, allow_ttl: int
    ) -> None:
        kernel = object.__getattribute__(self, "_kernel")
        permissions = getattr(kernel, "callback_permissions", None)
        if permissions is None:
            from ..base.permissions import CallbackPermissionManager

            permissions = CallbackPermissionManager()
            kernel.callback_permissions = permissions
        permissions.allow(user_id, token, allow_ttl)

    def set_live_module_config(self, module_name: str, config: Any) -> None:
        kernel = object.__getattribute__(self, "_kernel")
        live_configs = getattr(kernel, "_live_module_configs", None)
        if live_configs is None:
            live_configs = {}
            kernel._live_module_configs = live_configs
        live_configs[module_name] = config

    def get_live_module_config(self, module_name: str, default: Any = None) -> Any:
        kernel = object.__getattribute__(self, "_kernel")
        live_configs = getattr(kernel, "_live_module_configs", None) or {}
        return live_configs.get(module_name, default)

    def __getattribute__(self, name: str) -> Any:
        if name == "__dict__":
            _raise_insecure(name, object.__getattribute__(self, "_module_name"))
        if name in object.__getattribute__(self, "_LOCAL_NAMES"):
            return object.__getattribute__(self, name)
        if name in PROTECTED_KERNEL_NAMES or name.startswith("_"):
            _raise_insecure(name, object.__getattribute__(self, "_module_name"))
        module_state = object.__getattribute__(self, "_module_state")
        if name in module_state:
            return module_state[name]
        return getattr(object.__getattribute__(self, "_kernel"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_") or name in PROTECTED_KERNEL_NAMES:
            self._deny(name)
        object.__getattribute__(self, "_module_state")[name] = value

    def __delattr__(self, name: str) -> None:
        self._deny(name)

    def __dir__(self) -> list[str]:
        kernel = object.__getattribute__(self, "_kernel")
        names = set(dir(kernel)) - PROTECTED_KERNEL_NAMES
        names = {name for name in names if not name.startswith("_")}
        names.update(
            {
                "module_name",
                "register",
                "is_protected",
                "lookup_module",
                "get_loaded_module",
                "iter_loaded_module_names",
                "loaded_module_names",
                "loaded_modules_view",
                "system_modules_view",
                "_live_module_configs",
                "remove_inline_callback_tokens",
                "store_inline_callback",
                "allow_inline_callback_user",
                "set_live_module_config",
                "get_live_module_config",
            }
        )
        return sorted(names)

    def __repr__(self) -> str:
        return f"<ModuleKernelProxy module={self.module_name!r}>"


def get_module_kernel(kernel: Any, module_name: str, is_system: bool) -> Any:
    if is_system:
        return kernel
    return ModuleKernelProxy(kernel, module_name)


def get_module_register(kernel: Any, module_name: str, is_system: bool) -> Any:
    if is_system:
        return kernel.register
    return ModuleRegisterProxy(kernel.register, module_name)
