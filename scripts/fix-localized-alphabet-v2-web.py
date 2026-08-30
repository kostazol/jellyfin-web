#!/usr/bin/env python3
from pathlib import Path

p = Path('src/apps/modern/features/libraries/utils/alphabet.ts')
text = p.read_text(encoding='utf-8')
old = '''export const getAlphabetNavigationSettings = (\n    systemInfo?: AlphabetNavigationSystemInfo\n): AlphabetNavigationSettings => ({\n    enabled: Boolean(systemInfo?.EnableLocalizedAlphabetNavigation),\n    locale: systemInfo?.LocalizedAlphabetLocale ?? '',\n    additionalScripts: systemInfo?.LocalizedAlphabetAdditionalScripts ?? []\n});'''
new = '''export const getAlphabetNavigationSettings = (\n    systemInfo?: unknown\n): AlphabetNavigationSettings => {\n    const info = systemInfo as AlphabetNavigationSystemInfo | undefined;\n    return {\n        enabled: Boolean(info?.EnableLocalizedAlphabetNavigation),\n        locale: info?.LocalizedAlphabetLocale ?? '',\n        additionalScripts: info?.LocalizedAlphabetAdditionalScripts ?? []\n    };\n};'''
if new not in text:
    if old not in text:
        raise RuntimeError('getAlphabetNavigationSettings anchor not found')
    text = text.replace(old, new, 1)
p.write_text(text, encoding='utf-8')
