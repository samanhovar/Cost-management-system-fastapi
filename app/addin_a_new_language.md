# Adding a New Language

This project translates user-facing messages with **gettext** (`.po` / `.mo` files) and **Babel** (the `pybabel` command).
This document explains how it works and how to add a new language.

All commands below are run from inside the `app/` folder, with the virtual environment active.

---

## 1. How it works

| Piece | File | What it does |
|---|---|---|
| Supported languages | `core/dependencies.py` → `LanguageEnum` | The list of languages the project accepts (`en`, `fa`). Also holds `DEFAULT_LANGUAGE`. |
| Language detection | `core/dependencies.py` → `resolve_language`, `add_language_to_request` | A middleware that runs on every request and stores the result in `request.state.language`. |
| Translator | `core/i18n.py` → `get_translator` | Loads the `.mo` file of a language and returns the translate function `_`. |
| Translation files | `locales/<lang>/LC_MESSAGES/messages.po` and `.mo` | The actual translated texts. |
| Template | `locales/messages.pot` | The list of all translatable messages, generated from the code. |

### How the language is chosen (in this order)

1. The `lang` query parameter, e.g. `/costs/?lang=fa`
2. The `Accept-Language` header sent by the browser, e.g. `fa-IR,fa;q=0.9,en;q=0.8`
3. The default language (`en`)

A value that is not in `LanguageEnum` (e.g. `?lang=de` before German is added) is ignored and the next rule is used.

### How a route uses it

```python
from fastapi import Request
from core.i18n import get_translator

async def some_route(request: Request):
    _ = get_translator(request.state.language)
    return {"detail": _("object removed successfully")}
```

The English text inside `_("...")` is the key (`msgid`). It must be identical in the code and in the `.po` files.

---

## 2. Adding a new language

Example: adding German (`de`).

### Step 1: Register the language

In `core/dependencies.py`, add it to `LanguageEnum`:

```python
class LanguageEnum(str, Enum):
    en = "en"
    fa = "fa"
    de = "de"   # new
```

Use the short language code (two letters). The value is also the folder name inside `locales/`.

### Step 2: Refresh the template

This makes sure `messages.pot` contains every message currently in the code:

```bash
pybabel extract -o locales/messages.pot .
```

### Step 3: Create the language file

```bash
pybabel init -i locales/messages.pot -d locales -l de
```

This creates `locales/de/LC_MESSAGES/messages.po` with every message and an empty translation.

> Use `init` only once per language. Running it again on an existing language overwrites the translations already written. To update an existing language, use `update` (section 3).

### Step 4: Write the translations

Open `locales/de/LC_MESSAGES/messages.po` and fill in each `msgstr`:

```po
msgid "not found error"
msgstr "Nicht gefunden"
```

Rules:

- Never change the `msgid` line.
- Only write between the quotes of `msgstr`.
- Leave the header block at the top of the file alone.
- If an entry has a `#, fuzzy` comment above it, Babel guessed the translation. Check it, then delete the `#, fuzzy` line. Fuzzy entries are ignored when compiling.

### Step 5: Compile

```bash
pybabel compile -d locales
```

This creates `messages.mo`, the file the application actually reads.

### Step 6: Restart and test

Restart the server (translations are loaded once and cached), then test:

```
GET /?lang=de
```

and a request with the header `Accept-Language: de`. Both should return the German text.

### Checklist

- [ ] Added to `LanguageEnum`
- [ ] `locales/<lang>/LC_MESSAGES/messages.po` exists and is translated
- [ ] No leftover `#, fuzzy` entries
- [ ] `messages.mo` compiled
- [ ] Server restarted and tested with `?lang=` and with `Accept-Language`

---

## 3. Adding new messages to the project

When a route gets a new user-facing text:

1. Wrap it in `_("...")` in the code.
2. Extract: `pybabel extract -o locales/messages.pot .`
3. Update all existing languages (keeps old translations, adds new empty entries):
   `pybabel update -i locales/messages.pot -d locales`
4. Translate the new empty entries in every `.po` file.
5. Compile: `pybabel compile -d locales`
6. Restart the server.

A message that already exists is reused for free: the same `_("not found error")` in many routes is one entry.

---

## 4. Command cheat sheet

| Goal | Command |
|---|---|
| Collect messages from the code | `pybabel extract -o locales/messages.pot .` |
| Create a new language | `pybabel init -i locales/messages.pot -d locales -l <lang>` |
| Add new messages to existing languages | `pybabel update -i locales/messages.pot -d locales` |
| Compile translations | `pybabel compile -d locales` |

Every time a `.po` file is edited, run `compile` again and restart the server.

---

## 5. Troubleshooting

| Problem | Likely cause |
|---|---|
| The response is in English although the language is correct | `.mo` not compiled after the last edit, server not restarted, or the `msgid` differs from the text in the code (even one letter or a capital). |
| `FileNotFoundError: No translation file found for domain: 'messages'` | The `.mo` file is missing, or the folder is not exactly `locales/<lang>/LC_MESSAGES/messages.mo`. To debug, temporarily set `fallback=False` in `core/i18n.py`; set it back to `True` afterwards. |
| New language is ignored | It was not added to `LanguageEnum`. |
| A translation is not used after `update` | The entry is marked `#, fuzzy`. Fix the text and remove that line. |
| `pybabel: command not found` | The virtual environment is not active, or Babel is not installed (`pip install Babel`). |

---

## 6. Limitations

- Messages containing changing values (for example a username inside the text) need placeholders (`%(name)s`), which are not used in the project yet.
- Validation messages inside Pydantic schemas (for example `ValueError(...)` in a validator) have no access to the request, so they are not translated yet.
- Decide whether the compiled `.mo` files are committed to git or generated during deployment, and keep that consistent.
