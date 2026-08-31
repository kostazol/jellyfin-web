import { LibraryTab } from 'types/libraryTab';

export interface AlphabetPickerGroup {
    id: string;
    values: string[];
}

interface AlphabetDefinition extends AlphabetPickerGroup {
    localePrefixes: string[];
    script: string;
    aliases?: Partial<Record<string, string[]>>;
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
    values: 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'.split(''),
    aliases: {
        Α: ['Ά'],
        Ε: ['Έ'],
        Η: ['Ή'],
        Ι: ['Ί', 'Ϊ', 'ΐ'],
        Ο: ['Ό'],
        Σ: ['ς'],
        Υ: ['Ύ', 'Ϋ', 'ΰ'],
        Ω: ['Ώ']
    }
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
    values: 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЮЯ'.split(''),
    aliases: {
        И: ['Ѝ']
    }
};

const DEFINITIONS = [GREEK, CYRILLIC_RU, CYRILLIC_UK, CYRILLIC_BE, CYRILLIC_BG, LATIN];

// Additional scripts need a single unambiguous alphabet definition. Some
// scripts (for example Cyrillic) differ by locale, so they should not be
// guessed here until the UI can select a concrete alphabet definition.
const ADDITIONAL_DEFINITIONS: Record<string, AlphabetDefinition> = {
    Latn: LATIN
};

const LOCALIZED_ALPHABET_VIEW_TYPES = new Set<LibraryTab>([
    LibraryTab.Albums,
    LibraryTab.AlbumArtists,
    LibraryTab.Artists,
    LibraryTab.Books,
    LibraryTab.Collections,
    LibraryTab.Episodes,
    LibraryTab.Favorites,
    LibraryTab.Folders,
    LibraryTab.Genres,
    LibraryTab.Mixed,
    LibraryTab.Movies,
    LibraryTab.MusicVideos,
    LibraryTab.PhotoAlbums,
    LibraryTab.Photos,
    LibraryTab.Playlists,
    LibraryTab.Series,
    LibraryTab.Songs,
    LibraryTab.Studios,
    LibraryTab.Videos
]);

const normalizeLocale = (locale: string) => locale.replace(/_/g, '-').toLowerCase();

const getLegacyAlphabetQuery = (alphabet?: string | null): LegacyAlphabetQuery => ({
    nameLessThan: alphabet === '#' ? 'A' : undefined,
    nameStartsWith: alphabet === '#' ? undefined : (alphabet ?? undefined)
});

export const getAlphabetNavigationSettings = (
    systemInfo?: unknown
): AlphabetNavigationSettings => {
    const info = systemInfo as AlphabetNavigationSystemInfo | undefined;
    return {
        enabled: Boolean(info?.EnableLocalizedAlphabetNavigation),
        locale: info?.LocalizedAlphabetLocale ?? '',
        additionalScripts: info?.LocalizedAlphabetAdditionalScripts ?? []
    };
};

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

    const localeParts = normalizedLocale.split('-');
    if (localeParts.includes('latn')) {
        return LATIN;
    }

    return undefined;
};

export const supportsLocalizedAlphabetNavigation = (
    viewType: LibraryTab,
    settings: AlphabetNavigationSettings
) => LOCALIZED_ALPHABET_VIEW_TYPES.has(viewType)
    && Boolean(getPrimaryAlphabetDefinition(settings.locale));

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
        const definition = ADDITIONAL_DEFINITIONS[script];
        if (definition && !definitions.some(candidate => candidate.id === definition.id)) {
            definitions.push(definition);
        }
    }

    return definitions;
};

const getInitialGroup = (definition: AlphabetDefinition, value: string) => [
    value,
    ...(definition.aliases?.[value] ?? [])
];

const getOrderedInitials = (definitions: AlphabetDefinition[]) => [
    ...new Set(definitions.flatMap(definition =>
        definition.values.flatMap(value => getInitialGroup(definition, value))
    ))
];

const getOrderedInitialGroups = (definitions: AlphabetDefinition[]): string[] => {
    const seen = new Set<string>();
    const groups: string[] = [];

    for (const definition of definitions) {
        for (const value of definition.values) {
            const group = getInitialGroup(definition, value).filter(initial => {
                if (seen.has(initial)) {
                    return false;
                }

                seen.add(initial);
                return true;
            });

            if (group.length > 0) {
                groups.push(group.join('|'));
            }
        }
    }

    return groups;
};

const getSelectedInitials = (
    definitions: AlphabetDefinition[],
    selected: string
): string[] => {
    for (const definition of definitions) {
        for (const value of definition.values) {
            const initials = getInitialGroup(definition, value);
            if (initials.includes(selected)) {
                return initials;
            }
        }
    }

    return [];
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
    selectedAlphabet: string | null | undefined,
    settings: AlphabetNavigationSettings,
    viewType: LibraryTab
): AlphabetFilter => {
    const enabled = getEnabledAlphabets(settings, viewType);
    if (enabled.length === 0) {
        return { query: getLegacyAlphabetQuery(selectedAlphabet) };
    }

    const orderedInitials = getOrderedInitials(enabled);
    const orderedInitialGroups = getOrderedInitialGroups(enabled);

    if (!selectedAlphabet) {
        return {
            query: {},
            params: { nameInitialSortOrder: orderedInitialGroups.join(',') }
        };
    }

    if (selectedAlphabet === '#') {
        return {
            query: {},
            params: { excludeNameInitials: orderedInitials.join(',') }
        };
    }

    const selectedInitials = getSelectedInitials(enabled, selectedAlphabet);
    if (selectedInitials.length > 0) {
        return {
            query: {},
            params: { nameInitials: selectedInitials.join(',') }
        };
    }

    return {
        query: {},
        params: { nameInitialSortOrder: orderedInitialGroups.join(',') }
    };
};
