# Module Config API

← [Index](../../API_DOC.md)

MCUB provides two ways to configure modules: a simple dict-based API and a structured **ModuleConfig** system (recommended). Both are backed by the database and persist across restarts.

## Simple Dict API

`kernel.get_module_config(module_name, default=None)` - Retrieve the full config dict for a module.

`kernel.save_module_config(module_name, config_data)` - Save the full config dict for a module.

`kernel.get_module_config_key(module_name, key, default=None)` - Retrieve a single key from the module config.

`kernel.set_module_config_key(module_name, key, value)` - Set a single key in the module config without overwriting other keys.

`kernel.delete_module_config_key(module_name, key)` - Remove a single key from the module config.

`kernel.update_module_config(module_name, updates)` - Merge a dict of updates into the module config (shallow merge).

`kernel.delete_module_config(module_name)` - Delete the entire config for a module.

`kernel.store_module_config_schema(module_name, config)` - **REQUIRED for UI!** Store a live ModuleConfig schema for the UI.

---

## ModuleConfig (Recommended)

The recommended way to create module configuration. Provides:
- Declarative parameter definitions with validation
- Automatic display in **Modules Config** UI
- Typed values with Boolean, Integer, Float, String, Choice, MultiChoice, Secret support

### Available Validators

| Validator | Description |
|-----------|-------------|
| `Boolean(default=...)` | Boolean value (True/False) |
| `Integer(default=..., min=..., max=...)` | Integer number |
| `Float(default=..., min=..., max=...)` | Floating point number |
| `String(default=..., min_len=..., max_len=...)` | String value |
| `Choice(choices=[...], default=...)` | One of a list of choices |
| `MultiChoice(choices=[...], default=[...])` | List of choices |
| `Secret(default=...)` | Secret value (hidden in UI) |
| `Link(default=..., schemes=("http", "https"), require_netloc=True)` | Valid URL |
| `RegExp(pattern=..., default=..., flags=0, fullmatch=True)` | String that matches the given regular expression |
| `TelegramID(default=..., allow_zero=False)` | Telegram ID |
| `Union(*validators, default=...)` | Combines multiple validators, e.g. `Union(Integer(), Float())` |
| `NoneType()` | `None` / `null` value |
| `Emoji(default=..., min_count=1, max_count=None)` | Valid emoji or emoji sequence |
| `EntityLike(default=...)` | Telegram entity-like value: ID, `@username`, `t.me` link or URL |

### Usage (Class-Style — Recommended)

```python
from __future__ import annotations

from core.lib.loader.module_base import ModuleBase
from core.lib.loader.module_config import (
    Boolean,
    Choice,
    ConfigValue,
    Integer,
    ModuleConfig,
    String,
)


class MyModule(ModuleBase):
    name = "MyModule"
    version = "1.0.0"

    config = ModuleConfig(
        ConfigValue(
            "enabled",
            True,
            description="Enable module",
            validator=Boolean(default=True),
        ),
        ConfigValue(
            "api_key",
            "",
            description="API Key",
            validator=String(default=""),
        ),
        ConfigValue(
            "mode",
            "default",
            description="Operation mode",
            validator=Choice(
                choices=["default", "fast", "safe"],
                default="default",
            ),
        ),
    )

    async def on_load(self) -> None:
        """Load persisted config values from DB into ModuleConfig."""
        config_dict = await self.kernel.get_module_config(
            self.name, self.config.to_dict()
        )
        self.config.from_dict(config_dict)
        self.kernel.store_module_config_schema(self.name, self.config)
```

### Usage (Function-Style)

```python
from core.lib.loader.module_config import (
    Boolean,
    Choice,
    ConfigValue,
    ModuleConfig,
    String,
)


def register(kernel):
    config = ModuleConfig(
        ConfigValue(
            "enabled",
            True,
            description="Enable module",
            validator=Boolean(default=True),
        ),
        ConfigValue(
            "api_key",
            "",
            description="API Key",
            validator=String(default=""),
        ),
        ConfigValue(
            "mode",
            "default",
            description="Operation mode",
            validator=Choice(
                choices=["default", "fast", "safe"],
                default="default",
            ),
        ),
    )

    async def on_load():
        config_dict = await kernel.get_module_config(
            __name__, config.to_dict()
        )
        config.from_dict(config_dict)
        await kernel.save_module_config(__name__, config.to_dict())
        kernel.store_module_config_schema(__name__, config)

    kernel.register_on_load(on_load)
```

### ConfigValue Parameters

```python
ConfigValue(
    key,                    # str: Parameter name (required)
    default,                # Default value
    description="",         # str: Description for UI
    validator=None,         # Validator (Boolean, String, Choice, etc.)
    hidden=False,           # bool: Hide in UI
    on_change=None          # callable: Function on change (on_change(old, new))
)
```

### Important Notes

1. **Always call `config.to_dict()` before saving** - this adds the `__mcub_config__` marker
2. **`kernel.store_module_config_schema()` is REQUIRED** - without it, Choice fields won't have inline selection buttons
3. **Always use `ConfigValue` objects** inside `ModuleConfig()`, never pass validators (`Boolean`, `String`, etc.) directly — `ModuleConfig.__init__` expects `*ConfigValue`
4. **Read values via `self.config["key"]`** for class-style or `config["key"]` for function-style — always read from the live instance
5. **Use Choice instead of String for enums** — provides dropdown UI in the config panel
6. **Don't use `typing.List` for lists** — use `String` with JSON serialization instead
