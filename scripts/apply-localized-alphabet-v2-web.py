#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f'anchor not found in {path}: {old[:120]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


alphabet = r'''import type { LibraryViewSettings } from 'types/library';
import { LibraryTab } from 'types/libraryTab';

export interface AlphabetPickerGroup {
    id: string;
    values: string[];
}

interface AlphabetDefinition extends AlphabetPickerGroup {
    localePrefixes: string[];
    script: string;
}

export interface AlphabetNavigationSettings {
    enabled: boolean;
    locale: string;
    additionalScripts: string[];
}

interface AlphabetNavigationSystemInfo {
    EnableLocalizedAlphabetNavigation?: boolean;
    LocalizedAlphabetLocale?: string | null;
    LocalizedAlphabetAdditionalScripts?: string[] | null;
}

interface LegacyAlphabetQuery {
    nameLessThan?: string;
    nameStartsWith?: string;
}

interface AlphabetFilter {
    query: LegacyAlphabetQuery;
    params?: Record<string, string>;
}

const LATIN: AlphabetDefinition = {
    id: 'latin',
    script: 'Latn',
    localePrefixes: [],
    values: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')
};

const GREEK: AlphabetDefinition = {
    id: 'greek',
    script: 'Grek',
    localePrefixes: ['el'],
    values: 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'.split('')
};

const CYRILLIC_RU: AlphabetDefinition = {
    id: 'cyrillic-ru',
    script: 'Cyrl',
    localePrefixes: ['ru'],
    values: 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'.split('')
};

const CYRILLIC_UK: AlphabetDefinition = {
    id: 'cyrillic-uk',
    script: 'Cyrl',
    localePrefixes: ['uk'],
    values: 'АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ'.split('')
};

const CYRILLIC_BE: AlphabetDefinition = {
    id: 'cyrillic-be',
    script: 'Cyrl',
    localePrefixes: ['be'],
    values: 'АБВГДЕЁЖЗІЙКЛМНОПРСТУЎФХЦЧШЫЬЭЮЯ'.split('')
};

const CYRILLIC_BG: AlphabetDefinition = {
    id: 'cyrillic-bg',
    script: 'Cyrl',
    localePrefixes: ['bg'],
    values: 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЮЯ'.split('')
};

const DEFINITIONS = [GREEK, CYRILLIC_RU, CYRILLIC_UK, CYRILLIC_BE, CYRILLIC_BG, LATIN];
const UNSUPPORTED_NON_LATIN_LOCALES = ['ar', 'bn', 'fa', 'he', 'hi', 'ja', 'kk', 'ko', 'mr', 'ta', 'th', 'ur', 'zh'];

const normalizeLocale = (locale: string) => locale.replace('_', '-').toLowerCase();

const getLegacyAlphabetQuery = (settings: LibraryViewSettings): LegacyAlphabetQuery => {
    const alphabetValue = settings.Alphabet ?? undefined;
    return {
        nameLessThan: alphabetValue === '#' ? 'A' : undefined,
        nameStartsWith: alphabetValue === '#' ? undefined : alphabetValue
    };
};

export const getAlphabetNavigationSettings = (
    systemInfo?: AlphabetNavigationSystemInfo
): AlphabetNavigationSettings => ({
    enabled: Boolean(systemInfo?.EnableLocalizedAlphabetNavigation),
    locale: systemInfo?.LocalizedAlphabetLocale ?? '',
    additionalScripts: systemInfo?.LocalizedAlphabetAdditionalScripts ?? []
});

export const getPrimaryAlphabetDefinition = (locale: string): AlphabetPickerGroup | undefined => {
    const normalizedLocale = normalizeLocale(locale);
    const definition = DEFINITIONS.find(candidate =>
        candidate.localePrefixes.some(prefix =>
            normalizedLocale === prefix || normalizedLocale.startsWith(`${prefix}-`)
        )
    );

    if (definition) {
        return definition;
    }

    if (UNSUPPORTED_NON_LATIN_LOCALES.some(prefix =>
        normalizedLocale === prefix || normalizedLocale.startsWith(`${prefix}-`)
    )) {
        return undefined;
    }

    return LATIN;
};

export const supportsLocalizedAlphabetNavigation = (
    viewType: LibraryTab,
    settings: AlphabetNavigationSettings
) => viewType !== LibraryTab.Authors && Boolean(getPrimaryAlphabetDefinition(settings.locale));

const getEnabledAlphabets = (
    settings: AlphabetNavigationSettings,
    viewType: LibraryTab
): AlphabetDefinition[] => {
    if (!settings.enabled || !supportsLocalizedAlphabetNavigation(viewType, settings)) {
        return [];
    }

    const primary = getPrimaryAlphabetDefinition(settings.locale);
    if (!primary) {
        return [];
    }

    const primaryDefinition = DEFINITIONS.find(definition => definition.id === primary.id);
    if (!primaryDefinition) {
        return [];
    }

    const definitions = [primaryDefinition];
    for (const script of settings.additionalScripts) {
        const definition = DEFINITIONS.find(candidate => candidate.script === script);
        if (definition && !definitions.some(candidate => candidate.id === definition.id)) {
            definitions.push(definition);
        }
    }

    return definitions;
};

export const getLocalizedAlphabetGroups = (
    settings: AlphabetNavigationSettings,
    viewType: LibraryTab
): AlphabetPickerGroup[] | undefined => {
    const enabled = getEnabledAlphabets(settings, viewType);
    return enabled.length > 0 ?
        enabled.map(({ id, values }) => ({ id, values })) :
        undefined;
};

export const getAlphabetFilter = (
    libraryViewSettings: LibraryViewSettings,
    settings: AlphabetNavigationSettings,
    viewType: LibraryTab
): AlphabetFilter => {
    const enabled = getEnabledAlphabets(settings, viewType);
    if (enabled.length === 0) {
        return { query: getLegacyAlphabetQuery(libraryViewSettings) };
    }

    const orderedInitials = [...new Set(enabled.flatMap(alphabet => alphabet.values))];
    const params: Record<string, string> = {
        nameInitialSortOrder: orderedInitials.join(',')
    };
    const selected = libraryViewSettings.Alphabet;

    if (!selected) {
        return { query: {}, params };
    }

    if (selected === '#') {
        params.excludeNameInitials = orderedInitials.join(',');
        return { query: {}, params };
    }

    if (orderedInitials.includes(selected)) {
        params.nameInitials = selected;
    }

    return { query: {}, params };
};
'''
Path('src/apps/modern/features/libraries/utils/alphabet.ts').write_text(alphabet, encoding='utf-8')

tests = r'''import { describe, expect, it } from 'vitest';

import type { LibraryViewSettings } from 'types/library';
import { LibraryTab } from 'types/libraryTab';

import {
    getAlphabetFilter,
    getAlphabetNavigationSettings,
    getLocalizedAlphabetGroups,
    getPrimaryAlphabetDefinition
} from './alphabet';

const librarySettings = (alphabet?: string | null): LibraryViewSettings => ({
    SortBy: [],
    SortOrder: 'Ascending' as LibraryViewSettings['SortOrder'],
    StartIndex: 0,
    CardLayout: false,
    ImageType: 'Primary' as LibraryViewSettings['ImageType'],
    ViewMode: 'grid' as LibraryViewSettings['ViewMode'],
    ShowTitle: true,
    Alphabet: alphabet
});

const russian = {
    enabled: true,
    locale: 'ru-RU',
    additionalScripts: []
};

describe('localized alphabet navigation', () => {
    it('preserves the Russian alphabet order including Ё, Ч and Я', () => {
        const values = getPrimaryAlphabetDefinition('ru-RU')?.values ?? [];
        expect(values.indexOf('Ё')).toBe(values.indexOf('Е') + 1);
        expect(values.indexOf('Ч')).toBeGreaterThan(values.indexOf('Ц'));
        expect(values.at(-1)).toBe('Я');
    });

    it('keeps legacy filters unchanged while the global feature is disabled', () => {
        const filter = getAlphabetFilter(
            librarySettings('#'),
            { enabled: false, locale: 'ru-RU', additionalScripts: [] },
            LibraryTab.Movies
        );

        expect(filter.params).toBeUndefined();
        expect(filter.query).toEqual({ nameLessThan: 'A', nameStartsWith: undefined });
    });

    it('sends native initial ordering even when no bucket is selected', () => {
        const filter = getAlphabetFilter(librarySettings(null), russian, LibraryTab.Movies);
        const order = filter.params?.nameInitialSortOrder?.split(',') ?? [];

        expect(order[0]).toBe('А');
        expect(order.indexOf('Ч')).toBeGreaterThan(order.indexOf('Ц'));
        expect(order.at(-1)).toBe('Я');
    });

    it('uses # as Other while preserving the same native sort order', () => {
        const filter = getAlphabetFilter(librarySettings('#'), russian, LibraryTab.Movies);

        expect(filter.params?.excludeNameInitials).toBe(filter.params?.nameInitialSortOrder);
        expect(filter.params?.excludeNameInitials).toContain('Ё');
    });

    it('appends Latin after the primary alphabet when Latn is enabled', () => {
        const groups = getLocalizedAlphabetGroups(
            { ...russian, additionalScripts: ['Latn'] },
            LibraryTab.Movies
        );
        const filter = getAlphabetFilter(
            librarySettings(null),
            { ...russian, additionalScripts: ['Latn'] },
            LibraryTab.Movies
        );
        const order = filter.params?.nameInitialSortOrder?.split(',') ?? [];

        expect(groups).toHaveLength(2);
        expect(groups?.[0].values.at(-1)).toBe('Я');
        expect(groups?.[1].values[0]).toBe('A');
        expect(order.indexOf('A')).toBeGreaterThan(order.indexOf('Я'));
    });

    it('reads the global server configuration from SystemInfo', () => {
        expect(getAlphabetNavigationSettings({
            EnableLocalizedAlphabetNavigation: true,
            LocalizedAlphabetLocale: 'el-GR',
            LocalizedAlphabetAdditionalScripts: ['Latn']
        })).toEqual({
            enabled: true,
            locale: 'el-GR',
            additionalScripts: ['Latn']
        });
    });

    it('keeps Authors on the legacy API path', () => {
        const filter = getAlphabetFilter(librarySettings('O'), russian, LibraryTab.Authors);
        expect(filter.params).toBeUndefined();
        expect(filter.query.nameStartsWith).toBe('O');
    });
});
'''
Path('src/apps/modern/features/libraries/utils/alphabet.test.ts').write_text(tests, encoding='utf-8')

picker = r'''import React, { useCallback } from 'react';

import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

import type { AlphabetPickerGroup } from '../utils/alphabet';

import 'components/alphaPicker/style.scss';

interface AlphabetPickerProps {
    value?: string | null;
    onChange: (value: string | null | undefined) => void;
    groups?: AlphabetPickerGroup[];
}

const LETTER_VALUES = ['#', ...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')];

const AlphabetButtons = ({
    values,
    value,
    onChange
}: {
    values: string[];
    value?: string | null;
    onChange: (event: React.MouseEvent<HTMLElement>, value: string | null | undefined) => void;
}) => (
    <ToggleButtonGroup
        orientation='vertical'
        value={value}
        exclusive
        color='primary'
        size='small'
        onChange={onChange}
    >
        {values.map((letter) => (
            <ToggleButton
                key={letter}
                value={letter}
                sx={{
                    borderWidth: 0,
                    paddingTop: {
                        xs: 0,
                        md: 0.25
                    },
                    paddingBottom: {
                        xs: 0,
                        md: 0.25
                    },
                    paddingLeft: 0.5,
                    paddingRight: 0.5
                }}
            >
                {letter}
            </ToggleButton>
        ))}
    </ToggleButtonGroup>
);

const AlphabetPicker: React.FC<AlphabetPickerProps> = ({
    value,
    onChange,
    groups
}) => {
    const handleValue = useCallback(
        (
            event: React.MouseEvent<HTMLElement>,
            newValue: string | null | undefined
        ) => {
            onChange(newValue);
        },
        [onChange]
    );

    const localizedGroups = groups?.length ? groups : undefined;

    return (
        <Box
            className='alphaPicker-fixed-right'
            // eslint-disable-next-line react/jsx-no-bind
            sx={theme => ({
                position: 'fixed',
                top: {
                    xs: '144px',
                    sm: '96px'
                },
                bottom: 0,
                fontSize: '80%',
                display: 'flex',
                alignItems: {
                    xs: 'flex-start',
                    sm: 'center'
                },
                gap: localizedGroups ? 0.25 : undefined,
                zIndex: theme.zIndex.appBar - 1
            })}
        >
            {!localizedGroups ? (
                <Paper
                    elevation={0}
                    sx={{
                        borderRadius: 1,
                        overflow: 'hidden'
                    }}
                >
                    <AlphabetButtons values={LETTER_VALUES} value={value} onChange={handleValue} />
                </Paper>
            ) : localizedGroups.map((group, groupIndex) => (
                <Paper
                    key={group.id}
                    elevation={0}
                    sx={{
                        borderRadius: 1,
                        overflow: 'hidden'
                    }}
                >
                    <AlphabetButtons
                        values={groupIndex === 0 ? ['#', ...group.values] : group.values}
                        value={value}
                        onChange={handleValue}
                    />
                </Paper>
            ))}
        </Box>
    );
};

export default AlphabetPicker;
'''
Path('src/apps/modern/features/libraries/components/AlphabetPicker.tsx').write_text(picker, encoding='utf-8')

# ItemsView: read global SystemInfo and only change the picker definition, not per-library settings.
replace_once(
    'src/apps/modern/features/libraries/components/ItemsView.tsx',
    "import { getDefaultLibraryViewSettings } from 'apps/modern/features/libraries/utils/settings';\n",
    "import { getDefaultLibraryViewSettings } from 'apps/modern/features/libraries/utils/settings';\nimport { getAlphabetNavigationSettings, getLocalizedAlphabetGroups } from 'apps/modern/features/libraries/utils/alphabet';\n")
replace_once(
    'src/apps/modern/features/libraries/components/ItemsView.tsx',
    "import { useApi } from 'hooks/useApi';\n",
    "import { useApi } from 'hooks/useApi';\nimport { useSystemInfo } from 'hooks/useSystemInfo';\n")
replace_once(
    'src/apps/modern/features/libraries/components/ItemsView.tsx',
    "    const { __legacyApiClient__, user } = useApi();\n",
    "    const { __legacyApiClient__, user } = useApi();\n    const { data: systemInfo } = useSystemInfo();\n")
replace_once(
    'src/apps/modern/features/libraries/components/ItemsView.tsx',
    "    const hasSortName = !libraryViewSettings.SortBy.includes(ItemSortBy.Random);\n\n",
    """    const hasSortName = !libraryViewSettings.SortBy.includes(ItemSortBy.Random);\n    const alphabetNavigationSettings = useMemo(\n        () => getAlphabetNavigationSettings(systemInfo),\n        [systemInfo]\n    );\n    const alphabetGroups = useMemo(\n        () => getLocalizedAlphabetGroups(alphabetNavigationSettings, viewType),\n        [alphabetNavigationSettings, viewType]\n    );\n\n""")
replace_once(
    'src/apps/modern/features/libraries/components/ItemsView.tsx',
    """                <AlphabetPicker\n                    value={libraryViewSettings.Alphabet}\n                    onChange={handleAlphabetChange}\n                />\n""",
    """                <AlphabetPicker\n                    value={libraryViewSettings.Alphabet}\n                    onChange={handleAlphabetChange}\n                    groups={alphabetGroups}\n                />\n""")

# useFetchItems: global settings drive both filtering and native initial ordering.
p = Path('src/hooks/useFetchItems.ts')
text = p.read_text(encoding='utf-8')
text = text.replace(
    "import { getAlphaPickerQuery, getFieldsQuery, getFiltersQuery, getLimitQuery } from 'utils/items';",
    "import { getFieldsQuery, getFiltersQuery, getLimitQuery } from 'utils/items';\nimport { getAlphabetFilter, getAlphabetNavigationSettings, type AlphabetNavigationSettings } from 'apps/modern/features/libraries/utils/alphabet';")
text = text.replace(
    "import { type JellyfinApiContext, useApi } from './useApi';",
    "import { type JellyfinApiContext, useApi } from './useApi';\nimport { useSystemInfo } from './useSystemInfo';")
old_sig = '''    itemType: BaseItemKind[],\n    libraryViewSettings: LibraryViewSettings,\n    options?: AxiosRequestConfig\n) => {\n    const { api, user } = currentApi;\n    if (api && user?.Id && viewType) {\n        const isFavorite'''
new_sig = '''    itemType: BaseItemKind[],\n    libraryViewSettings: LibraryViewSettings,\n    alphabetNavigationSettings: AlphabetNavigationSettings,\n    options?: AxiosRequestConfig\n) => {\n    const { api, user } = currentApi;\n    if (api && user?.Id && viewType) {\n        const alphabetFilter = getAlphabetFilter(\n            libraryViewSettings,\n            alphabetNavigationSettings,\n            viewType\n        );\n        const requestOptions: AxiosRequestConfig = {\n            signal: options?.signal,\n            params: alphabetFilter.params\n        };\n        const isFavorite'''
if old_sig not in text:
    raise RuntimeError('useFetchItems function signature anchor not found')
text = text.replace(old_sig, new_sig, 1)
start = text.index('const fetchGetItemsViewByType')
end = text.index('export const useGetItemsViewByType', start)
segment = text[start:end]
segment = segment.replace('...getAlphaPickerQuery(libraryViewSettings),', '...alphabetFilter.query,')
segment = segment.replace("{\n                        signal: options?.signal\n                    }", 'requestOptions')
text = text[:start] + segment + text[end:]
old_hook = '''    const currentApi = useApi();\n    return useQuery({\n        queryKey: ['''
new_hook = '''    const currentApi = useApi();\n    const { data: systemInfo } = useSystemInfo();\n    const alphabetNavigationSettings = getAlphabetNavigationSettings(systemInfo);\n    return useQuery({\n        queryKey: ['''
if old_hook not in text:
    raise RuntimeError('useGetItemsViewByType hook anchor not found')
# Replace only the occurrence after export const useGetItemsViewByType.
hook_pos = text.index('export const useGetItemsViewByType')
pos = text.index(old_hook, hook_pos)
text = text[:pos] + text[pos:].replace(old_hook, new_hook, 1)
text = text.replace(
    '''                itemType,\n                libraryViewSettings\n            }\n''',
    '''                itemType,\n                libraryViewSettings,\n                alphabetNavigationSettings\n            }\n''',
    1)
text = text.replace(
    '''                itemType,\n                libraryViewSettings!,\n                { signal }\n''',
    '''                itemType,\n                libraryViewSettings!,\n                alphabetNavigationSettings,\n                { signal }\n''',
    1)
text = text.replace(
    '        enabled: !!currentApi.api && !!currentApi.user?.Id\n            && viewType\n',
    '        enabled: !!currentApi.api && !!currentApi.user?.Id && !!systemInfo\n            && viewType\n',
    1)
p.write_text(text, encoding='utf-8')

# Dashboard > General: global settings immediately below display language.
p = Path('src/apps/dashboard/routes/settings/index.tsx')
text = p.read_text(encoding='utf-8')
interface_anchor = "import { ActionData } from 'types/actionData';\n"
interface_text = interface_anchor + '''\ninterface LocalizedAlphabetConfiguration {\n    EnableLocalizedAlphabetNavigation?: boolean;\n    LocalizedAlphabetAdditionalScripts?: string[] | null;\n}\n'''
if 'interface LocalizedAlphabetConfiguration' not in text:
    text = text.replace(interface_anchor, interface_text, 1)
text = text.replace(
    "    config.UICulture = formData.get('UICulture')?.toString();\n",
    """    config.UICulture = formData.get('UICulture')?.toString();\n    const localizedAlphabetConfig = config as typeof config & LocalizedAlphabetConfiguration;\n    localizedAlphabetConfig.EnableLocalizedAlphabetNavigation =\n        formData.get('EnableLocalizedAlphabetNavigation')?.toString() === 'on';\n    localizedAlphabetConfig.LocalizedAlphabetAdditionalScripts =\n        formData.get('IncludeLatinAlphabet')?.toString() === 'on' ? ['Latn'] : [];\n""",
    1)
component_anchor = "    const [ metadataPath, setMetadataPath ] = useState<string | null | undefined>('');\n"
if 'const localizedAlphabetConfig = config as typeof config & LocalizedAlphabetConfiguration;' not in text[text.index('export const Component'):]:
    text = text.replace(
        component_anchor,
        component_anchor + "    const localizedAlphabetConfig = config as typeof config & LocalizedAlphabetConfiguration;\n",
        1)
ui_anchor = '''                            </TextField>\n\n                            <Typography variant='h2'>{globalize.translate('HeaderPaths')}</Typography>\n'''
ui_new = '''                            </TextField>\n\n                            <FormControl>\n                                <FormControlLabel\n                                    control={\n                                        <Checkbox\n                                            name='EnableLocalizedAlphabetNavigation'\n                                            defaultChecked={localizedAlphabetConfig.EnableLocalizedAlphabetNavigation}\n                                        />\n                                    }\n                                    label={globalize.translate('UseLocalizedAlphabetNavigation')}\n                                />\n                                <FormControlLabel\n                                    control={\n                                        <Checkbox\n                                            name='IncludeLatinAlphabet'\n                                            defaultChecked={localizedAlphabetConfig.LocalizedAlphabetAdditionalScripts?.includes('Latn')}\n                                        />\n                                    }\n                                    label={globalize.translate('IncludeLatinAlphabet')}\n                                />\n                            </FormControl>\n\n                            <Typography variant='h2'>{globalize.translate('HeaderPaths')}</Typography>\n'''
if "name='EnableLocalizedAlphabetNavigation'" not in text:
    if ui_anchor not in text:
        raise RuntimeError('dashboard settings UI anchor not found')
    text = text.replace(ui_anchor, ui_new, 1)
p.write_text(text, encoding='utf-8')

# Add only two translation lines without reformatting translation files.
def add_translations(path: str, translations: dict[str, str]) -> None:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    missing = [(key, value) for key, value in translations.items() if f'"{key}"' not in text]
    if not missing:
        return
    lines = text.splitlines()
    insert_at = len(lines) - 1
    if insert_at <= 0 or lines[-1].strip() != '}':
        raise RuntimeError(f'unexpected JSON layout: {path}')
    # Add a comma to the previous final property if needed, then append new properties.
    if not lines[insert_at - 1].rstrip().endswith(','):
        lines[insert_at - 1] = lines[insert_at - 1] + ','
    for index, (key, value) in enumerate(missing):
        comma = ',' if index < len(missing) - 1 else ''
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        lines.insert(insert_at + index, f'    "{key}": "{escaped}"{comma}')
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')

add_translations('src/strings/en-us.json', {
    'UseLocalizedAlphabetNavigation': 'Use localized alphabet navigation',
    'IncludeLatinAlphabet': 'Include Latin alphabet (A–Z)'
})
add_translations('src/strings/ru.json', {
    'UseLocalizedAlphabetNavigation': 'Использовать локализованную навигацию по алфавиту',
    'IncludeLatinAlphabet': 'Добавить латинский алфавит (A–Z)'
})
