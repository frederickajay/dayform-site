#!/usr/bin/env python3 -I
"""Builds g/index.html (the "Gift a friend" landing page) from template.html, strings-new.json and the app's catalog.

Usage: python3 -I g/build.py <path to Resources/Localizable.xcstrings>
The texts the app already has (the friend's screens) come from its catalog, so the page and the app say the same thing
in every language; the few page-only texts are in strings-new.json. Fails if any text is missing in any language.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = ["en", "es", "fr", "de", "pt-BR", "it", "nl", "pl", "tr", "ru", "uk", "ar", "ja", "ko", "zh-Hans", "zh-Hant",
         "id", "vi", "th"]
FROM_APP = {
    "from": "A gift from %@",
    "forYou": "A gift for you",
    "for": "For %@",
    "year": "A year of Dayform",
    "yours": "A year of Dayform is yours.",
    "tell": "Let %@ know it was opened",
    "tellAny": "Let them know it was opened",
    "claim": "Claim with Apple",
    "waiting": "Something's waiting for you",
    "opensIn": "Opens in %@",
    "cancelled": "This gift was cancelled by the person who sent it.",
    "expired": "This gift has expired. The person who sent it can ask Apple for a refund.",
    "claimed": "This gift has already been opened on another iPhone or Apple Account.",
    "later": "Your gift is safe. We're getting it ready, please try again in a little while.",
    "paused": "Gifts are taking a short break. Your gift is safe; please try again later.",
    "usedTwo": "This Apple Account has already used two Dayform gifts. %@ can ask Apple for a refund.",
    "usedTwoAny": "This Apple Account has already used two Dayform gifts. The person who sent it can ask Apple for a refund.",
    "broken": "This gift link isn't complete. Ask the person who sent it to share it again.",
    "offline": "Connect to the internet to open your gift.",
    "unreachable": "Dayform could not reach the gift service. Nothing is lost; try again when you are online.",
}


def main(catalog_path):
    catalog = json.load(open(catalog_path, encoding="utf-8"))["strings"]
    strings, missing = {}, []
    for key, english in FROM_APP.items():
        entry = catalog.get(english) or catalog.get(english.replace("'", "’"))
        if entry is None:
            missing.append(f"catalog has no key {english!r}")
            continue
        loc = entry.get("localizations", {})
        strings[key] = {}
        for lang in LANGS:
            unit = loc.get(lang, {}).get("stringUnit", {})
            value = unit.get("value") if unit.get("state") in (None, "translated", "needs_review") else None
            if lang == "en":
                value = value or english
            if not value:
                missing.append(f"{key} [{lang}]")
                continue
            strings[key][lang] = value.replace("%1$@", "%@")
    for key, values in json.load(open(os.path.join(HERE, "strings-new.json"), encoding="utf-8")).items():
        if key.startswith("_"):
            continue
        for lang in LANGS:
            if not values.get(lang):
                missing.append(f"{key} [{lang}]")
        strings[key] = values
    if missing:
        raise SystemExit("missing:\n  " + "\n  ".join(missing))
    template = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    blob = json.dumps(strings, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    page = template.replace("/*STRINGS*/{}", blob, 1)
    assert page != template, "STRINGS marker not found"
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
    print(f"wrote g/index.html: {len(strings)} texts x {len(LANGS)} languages")


if __name__ == "__main__":
    main(sys.argv[1])
