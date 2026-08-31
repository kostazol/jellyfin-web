#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
path = root / 'src/apps/modern/features/libraries/utils/alphabet.ts'
text = path.read_text()

# The server persists the lower-cased NFC first rune. Include lower-case precomposed
# monotonic forms that do not have a single-code-point uppercase equivalent, and the
# Bulgarian grave-marked I which alphabetically belongs to И rather than Other.
text = text.replace("        Ι: ['Ί', 'Ϊ'],\n", "        Ι: ['Ί', 'Ϊ', 'ΐ'],\n", 1)
text = text.replace("        Υ: ['Ύ', 'Ϋ'],\n", "        Υ: ['Ύ', 'Ϋ', 'ΰ'],\n", 1)
text = text.replace(
    "    values: 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЮЯ'.split('')\n};\n",
    "    values: 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЮЯ'.split(''),\n    aliases: {\n        И: ['Ѝ']\n    }\n};\n",
    1)

ordered_initials = '''const getOrderedInitials = (definitions: AlphabetDefinition[]) => [\n    ...new Set(definitions.flatMap(definition =>\n        definition.values.flatMap(value => getInitialGroup(definition, value))\n    ))\n];\n'''
ordered_groups = ordered_initials + '''\nconst getOrderedInitialGroups = (definitions: AlphabetDefinition[]): string[] => {\n    const seen = new Set<string>();\n    const groups: string[] = [];\n\n    for (const definition of definitions) {\n        for (const value of definition.values) {\n            const group = getInitialGroup(definition, value).filter(initial => {\n                if (seen.has(initial)) {\n                    return false;\n                }\n\n                seen.add(initial);\n                return true;\n            });\n\n            if (group.length > 0) {\n                groups.push(group.join('|'));\n            }\n        }\n    }\n\n    return groups;\n};\n'''
if ordered_initials not in text:
    raise SystemExit('Expected ordered initials helper not found')
text = text.replace(ordered_initials, ordered_groups, 1)

old_filter_start = '''    const orderedInitials = getOrderedInitials(enabled);\n\n    if (!selectedAlphabet) {\n        return {\n            query: {},\n            params: { nameInitialSortOrder: orderedInitials.join(',') }\n        };\n    }\n'''
new_filter_start = '''    const orderedInitials = getOrderedInitials(enabled);\n    const orderedInitialGroups = getOrderedInitialGroups(enabled);\n\n    if (!selectedAlphabet) {\n        return {\n            query: {},\n            params: { nameInitialSortOrder: orderedInitialGroups.join(',') }\n        };\n    }\n'''
if old_filter_start not in text:
    raise SystemExit('Expected localized ordering block not found')
text = text.replace(old_filter_start, new_filter_start, 1)

old_fallback = '''    return {\n        query: {},\n        params: { nameInitialSortOrder: orderedInitials.join(',') }\n    };\n};\n'''
new_fallback = '''    return {\n        query: {},\n        params: { nameInitialSortOrder: orderedInitialGroups.join(',') }\n    };\n};\n'''
if old_fallback not in text:
    raise SystemExit('Expected localized ordering fallback not found')
path.write_text(text.replace(old_fallback, new_fallback, 1))

test_path = root / 'src/apps/modern/features/libraries/utils/alphabet.test.ts'
tests = test_path.read_text()
old_test = '''    it('keeps Greek accent aliases next to their base letter in unfiltered ordering', () => {\n        const filter = getAlphabetFilter(null, greek, LibraryTab.Movies);\n        const order = filter.params?.nameInitialSortOrder?.split(',') ?? [];\n\n        expect(order.indexOf('Ά')).toBe(order.indexOf('Α') + 1);\n        expect(order.indexOf('Β')).toBe(order.indexOf('Ά') + 1);\n        expect(order.indexOf('Ώ')).toBeGreaterThan(order.indexOf('Ω'));\n    });\n'''
new_test = '''    it('serializes Greek aliases as one sorting rank per visual bucket', () => {\n        const filter = getAlphabetFilter(null, greek, LibraryTab.Movies);\n        const order = filter.params?.nameInitialSortOrder?.split(',') ?? [];\n\n        expect(order[0]).toBe('Α|Ά');\n        expect(order[1]).toBe('Β');\n        expect(order).toContain('Ι|Ί|Ϊ|ΐ');\n        expect(order).toContain('Σ|ς');\n        expect(order).toContain('Υ|Ύ|Ϋ|ΰ');\n        expect(order.at(-1)).toBe('Ω|Ώ');\n    });\n\n    it('selecting a Greek alias resolves to the same visual bucket', () => {\n        const filter = getAlphabetFilter('ΐ', greek, LibraryTab.Movies);\n        expect(filter.params?.nameInitials?.split(',')).toEqual(['Ι', 'Ί', 'Ϊ', 'ΐ']);\n        expect(filter.params?.nameInitialSortOrder).toBeUndefined();\n    });\n'''
if old_test not in tests:
    raise SystemExit('Expected Greek ordering alias test not found')
tests = tests.replace(old_test, new_test, 1)
tests = tests.replace(
    "        expect(order.indexOf('A')).toBeGreaterThan(order.indexOf('Ώ'));\n",
    "        expect(order.indexOf('A')).toBeGreaterThan(order.indexOf('Ω|Ώ'));\n",
    1)

bulgarian_anchor = '''    it('keeps legacy filters unchanged while the global feature is disabled', () => {\n'''
bulgarian_test = '''    it('keeps Bulgarian grave-marked И in the И bucket', () => {\n        const bulgarian = { enabled: true, locale: 'bg-BG', additionalScripts: [] };\n        const selected = getAlphabetFilter('И', bulgarian, LibraryTab.Movies);\n        const order = getAlphabetFilter(null, bulgarian, LibraryTab.Movies)\n            .params?.nameInitialSortOrder?.split(',') ?? [];\n\n        expect(selected.params?.nameInitials?.split(',')).toEqual(['И', 'Ѝ']);\n        expect(order).toContain('И|Ѝ');\n    });\n\n'''
if bulgarian_anchor not in tests:
    raise SystemExit('Bulgarian test insertion point not found')
test_path.write_text(tests.replace(bulgarian_anchor, bulgarian_test + bulgarian_anchor, 1))
