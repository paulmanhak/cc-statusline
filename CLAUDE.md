# cc_status – Claude Code Statusline

Python skript zobrazující stav aktuální Claude Code relace jako jeden řádek v terminálu.

## Soubory

- `cc_status.py` – jediný zdrojový soubor; čte JSON ze stdin, vypisuje statusline
- `README.md` – uživatelská dokumentace (instalace, konfigurace)
- `CLAUDE.md` – tento soubor; technické detaily pro práci v Claude Code

## Jak to funguje

Claude Code spouští příkaz z `statusLine.command` při každém refreshi a posílá skriptu přes **stdin** JSON objekt s daty aktuální relace. Každý běžící agent dostává svá vlastní data – skript nečte žádné soubory z disku.

Původní verze skriptu četla soubory přímo z `~/.claude/projects/`, což způsobovalo, že všechny souběžně běžící agenty zobrazovaly stejná data (z nejnovějšího souboru). Přepis na stdin tento problém řeší.

### Vstupní schéma (stdin)

```json
{
  "session_id": "...",
  "transcript_path": "/home/.../.claude/projects/.../session.jsonl",
  "cwd": "/home/...",
  "model": { "id": "claude-sonnet-4-6", "display_name": "Sonnet 4.6" },
  "workspace": { "current_dir": "...", "project_dir": "...", "added_dirs": [] },
  "version": "2.1.90",
  "cost": { "total_cost_usd": 0.56, "total_duration_ms": 743274, ... },
  "context_window": {
    "context_window_size": 200000,
    "used_percentage": 17,
    "remaining_percentage": 83,
    "current_usage": {
      "input_tokens": 1,
      "cache_creation_input_tokens": 194,
      "cache_read_input_tokens": 33389,
      "output_tokens": 162
    }
  },
  "rate_limits": {
    "five_hour": { "used_percentage": 19, "resets_at": 1775149200 },
    "seven_day": { "used_percentage": 6,  "resets_at": 1775635200 }
  }
}
```

### Výstupní formát

```
Sonnet 4.6 | Kontext [██░░░░░░░░] 17% | Tokeny [██░░░░░░░░] 19% reset 03:24 | ~/Prj/skoleni2
```

| Pole | Zdroj v JSON |
|------|-------------|
| Model | `model.display_name` |
| Kontext teploměr | `context_window.used_percentage` |
| Tokeny teploměr | `rate_limits.five_hour.used_percentage` (fallback: `seven_day`) |
| Čas resetu | `rate_limits.five_hour.resets_at` (Unix timestamp → HH:MM) |
| Cesta | `workspace.current_dir` zkrácená na `~/...` |

### Barevné kódování teploměrů

Teploměry používají ANSI escape kódy; barva se volí podle aktuální hodnoty:

| Rozsah | Barva |
|--------|-------|
| 0–50 % | zelená (`\033[32m`) |
| 51–80 % | žlutá (`\033[33m`) |
| > 80 % | červená (`\033[31m`) |

## Konfigurace v Claude Code

Aktivní přes `~/.claude/settings.json`:

```json
"statusLine": {
  "type": "command",
  "command": "python3 /home/paulman/Prj/skoleni2/cc_status.py"
}
```

## Ladění

### Zachycení stdin dat

Dočasně přepnout `settings.json` na debug skript:

```json
"command": "python3 /tmp/cc_status_debug.py"
```

Obsah `/tmp/cc_status_debug.py`:

```python
import os, sys, json
data = {
    "stdin": sys.stdin.read() if not sys.stdin.isatty() else "(tty)",
    "env": {k: v for k, v in os.environ.items() if "CLAUDE" in k},
    "cwd": os.getcwd(),
}
with open("/tmp/cc_status_debug.json", "w") as f:
    json.dump(data, f, indent=2)
print("ok")
```

### Testování s zachycenými daty

```bash
python3 -c "import json; d=json.load(open('/tmp/cc_status_debug.json')); print(d['stdin'],end='')" \
  | python3 cc_status.py
```

### Ruční testování s vlastním JSON

```bash
echo '{"model":{"display_name":"Opus 4.6"},"context_window":{"used_percentage":85},"rate_limits":{"five_hour":{"used_percentage":60,"resets_at":9999999999}},"workspace":{"current_dir":"/home/paulman/test"}}' \
  | python3 cc_status.py
```
