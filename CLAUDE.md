# cc_status – Claude Code Statusline

Python skript zobrazující stav aktuální Claude Code relace jako jeden řádek v terminálu.

## Soubory

- `cc_status.py` – jediný soubor projektu; čte JSON ze stdin, vypisuje statusline

## Jak to funguje

Claude Code spouští skript při každém refreshi statusline a posílá mu přes **stdin** JSON objekt s daty aktuální relace. Každý běžící agent dostává svá vlastní data – skript nečte žádné soubory z disku.

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
    "current_usage": { "input_tokens": 1, "cache_creation_input_tokens": 194, "cache_read_input_tokens": 33389, "output_tokens": 162 }
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

- **Model** – `model.display_name`
- **Kontext** – teploměr + `context_window.used_percentage`
- **Tokeny** – teploměr + `rate_limits.five_hour.used_percentage` + čas do resetu (z `resets_at` unixtimestamp); fallback na `seven_day`
- **Cesta** – `workspace.current_dir` zkrácená na `~/...`

## Konfigurace v Claude Code

Aktivní přes `~/.claude/settings.json`:

```json
"statusLine": {
  "type": "command",
  "command": "python3 /home/paulman/Prj/skoleni2/cc_status.py"
}
```

## Spuštění / ladění

```bash
# Otestovat s reálnými daty z posledního debug zachycení
python3 -c "import json; d=json.load(open('/tmp/cc_status_debug.json')); print(d['stdin'],end='')" \
  | python3 cc_status.py

# Zachytit aktuální stdin data (dočasně přepnout v settings.json)
# "command": "python3 /tmp/cc_status_debug.py"
```

Debug skript `/tmp/cc_status_debug.py` zapíše přijatý JSON do `/tmp/cc_status_debug.json`.
