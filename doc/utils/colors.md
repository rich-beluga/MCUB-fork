# Colors - Terminal Output Styling

← [Index](../../API_DOC.md)

The `Colors` class provides ANSI terminal color codes and gradient effects for console output.

```python
from core.lib.utils.colors import Colors
```

---

## Color Constants

### Standard Colors

| Attribute | Code |
|-----------|------|
| `Colors.BLACK` | `\033[30m` |
| `Colors.RED` | `\033[31m` |
| `Colors.GREEN` | `\033[32m` |
| `Colors.YELLOW` | `\033[33m` |
| `Colors.BLUE` | `\033[34m` |
| `Colors.PURPLE` | `\033[35m` |
| `Colors.CYAN` | `\033[36m` |
| `Colors.WHITE` | `\033[37m` |

### Bright Colors

`Colors.BRIGHT_BLACK`, `Colors.BRIGHT_RED`, `Colors.BRIGHT_GREEN`, `Colors.BRIGHT_YELLOW`, `Colors.BRIGHT_BLUE`, `Colors.BRIGHT_PURPLE`, `Colors.BRIGHT_CYAN`, `Colors.BRIGHT_WHITE`

### Background Colors

`Colors.BG_BLACK`, `Colors.BG_RED`, `Colors.BG_GREEN`, `Colors.BG_BLUE`, `Colors.BG_PURPLE`, `Colors.BG_CYAN`, `Colors.BG_WHITE`, `Colors.BG_BRIGHT_BLACK`... and more.

### Named Utility Colors

| Attribute | Purpose |
|-----------|---------|
| `Colors.SUCCESS` | ✅ Bright green |
| `Colors.ERROR` | ❌ Bright red |
| `Colors.WARNING` | ⚠️ Bright yellow |
| `Colors.INFO` | ℹ️ Bright cyan |
| `Colors.DEBUG` | 🔍 Bright purple |
| `Colors.MUTED` | Dim grey |

### Named Extended Colors

`Colors.ORANGE`, `Colors.LIME`, `Colors.TEAL`, `Colors.MAROON`, `Colors.NAVY`, `Colors.GOLD`, `Colors.VIOLET`, `Colors.INDIGO`, `Colors.BROWN`, `Colors.SILVER`, `Colors.PINK`, `Colors.MAGENTA`, `Colors.GREY`/`Colors.GRAY`

### Text Styles

| Attribute | Effect |
|-----------|--------|
| `Colors.BOLD` | Bold text |
| `Colors.DIM` | Dimmed text |
| `Colors.ITALIC` | Italic text |
| `Colors.UNDERLINE` | Underlined text |
| `Colors.BLINK` | Blinking text |
| `Colors.STRIKETHROUGH` | Strikethrough |
| `Colors.OVERLINE` | Overline |
| `Colors.HIDDEN` | Hidden text |
| `Colors.REVERSE` | Swap fg/bg colors |

---

## Static Methods

### `Colors.paint(text, *codes) -> str`

Apply one or more color/style codes to text.

```python
colored = Colors.paint("Hello", Colors.RED, Colors.BOLD)
print(colored)
```

### `Colors.strip(text) -> str`

Remove all ANSI escape codes from a string.

```python
clean = Colors.strip("\033[31mHello\033[0m")
# -> "Hello"
```

### `Colors.rgb(r, g, b) -> str`

Generate 24-bit foreground color escape code.

```python
custom_red = Colors.rgb(255, 100, 50)
print(f"{custom_red}Custom color{Colors.RESET}")
```

### `Colors.rgb_bg(r, g, b) -> str`

Generate 24-bit background color escape code.

### `Colors.color256(n) -> str`

Generate 8-bit (256) foreground color escape code.

### `Colors.color256_bg(n) -> str`

Generate 8-bit background color escape code.

### `Colors.hex(code) -> str`

Generate foreground color from hex code (`"#FF5500"` or `"FF5500"`).

```python
print(f"{Colors.hex('#FF5500')}Orange text{Colors.RESET}")
```

### `Colors.hex_bg(code) -> str`

Generate background color from hex code.

---

## Gradient Methods

### `Colors.gradient(text, start_color, end_color, *, bold=False) -> str`

Apply a linear gradient from `start_color` to `end_color` across the text. Colors can be ANSI names or hex strings.

```python
text = Colors.gradient("Hello World", "red", "blue", bold=True)
print(text)
```

### `Colors.gradient_multicolor(text, colors, *, bold=False) -> str`

Apply a multi-stop gradient across the text.

```python
text = Colors.gradient_multicolor("Rainbow!", ["red", "yellow", "green", "blue"], bold=True)
print(text)
```

### `Colors.gradient_line(text, start_color, end_color, *, bold=False) -> str`

Apply gradient per character (not per word). Produces smoother transitions.

---

## Built-in Gradient Presets

| Method | Effect |
|--------|--------|
| `Colors.fire(text, bold=True)` | 🔥 Red → Yellow → Orange |
| `Colors.ocean(text, bold=False)` | 🌊 Blue → Cyan → Teal |
| `Colors.forest(text, bold=False)` | 🌲 Green → Lime |
| `Colors.sunset(text, bold=False)` | 🌅 Orange → Purple → Pink |
| `Colors.aurora(text, bold=False)` | 🌌 Green → Cyan → Blue → Purple |
| `Colors.neon(text, bold=True)` | 💡 Bright Pink → Cyan |
| `Colors.candy(text, bold=False)` | 🍬 Pink → Yellow → Cyan |
| `Colors.gold_gradient(text, bold=True)` | 🥇 Yellow → Gold → Orange |
| `Colors.ice(text, bold=False)` | ❄️ Light Blue → White → Cyan |
| `Colors.lava(text, bold=True)` | 🌋 Red → Orange → Dark Red |
| `Colors.matrix(text, bold=False)` | 💚 Green → Bright Green |
| `Colors.rose(text, bold=False)` | 🌹 Pink → Red |
| `Colors.rainbow(text, bold=False)` | 🌈 Full rainbow across text |

```python
print(Colors.fire("🔥 WARNING"))
print(Colors.rainbow("🌈 Rainbow text!"))
print(Colors.ocean("🌊 Oceanic"))
```

---

## Utility Methods

### `Colors.print_gradients()`

Print all gradient presets to console for preview.

### `Colors.print_palette()`

Print all color constants as a color palette preview.
