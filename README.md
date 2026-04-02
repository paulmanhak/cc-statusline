# cc_status

Statusline skript pro [Claude Code](https://claude.ai/code) zobrazující stav aktuální relace jako jeden řádek v terminálu.

```
Sonnet 4.6 | Kontext [██░░░░░░░░] 17% | Tokeny [██░░░░░░░░] 19% Reset za 2h 48min | ~/Prj/skoleni2
```

## Co zobrazuje

| Pole | Popis |
|------|-------|
| **Model** | Název aktuálně používaného modelu |
| **Kontext** | Zaplnění kontextového okna (teploměr + %) |
| **Tokeny** | Spotřeba 5hodinového rate limitu (teploměr + %) + čas do resetu |
| **Cesta** | Aktuální pracovní adresář zkrácený na `~/...` |

Teploměry jsou barevné: zelená ≤ 50 %, žlutá 51–80 %, červená > 80 %.

## Požadavky

- Python 3.6+
- Claude Code 2.x

## Instalace

1. Zkopíruj `cc_status.py` kamkoli, např. do `~/.claude/cc_status.py`
2. Uprav `~/.claude/settings.json` (viz níže)
3. Restartuj Claude Code

## Konfigurace settings.json

Otevři `~/.claude/settings.json` a přidej klíč `statusLine`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 /home/paulman/.claude/cc_status.py"
  }
}
```

Cestu v `command` uprav podle toho, kam jsi soubor zkopíroval.

### Ukázka kompletního settings.json

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 /home/paulman/.claude/cc_status.py"
  },
  "enabledPlugins": {
    "chrome-devtools-mcp@claude-plugins-official": true
  }
}
```

> **Poznámka:** Pokud soubor `settings.json` neexistuje, vytvoř ho s výše uvedeným obsahem.

## Jak to funguje

Claude Code spouští příkaz z `statusLine.command` při každém refreshi a posílá skriptu přes stdin JSON s daty aktuální relace. Díky tomu každý běžící agent zobrazuje svá vlastní data (správný kontext, adresář atd.).
