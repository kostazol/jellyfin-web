from __future__ import annotations

import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()


def write(relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


write(
    'src/apps/modern/features/libraries/utils/alphabet.ts',
    '''import { LibraryTab } from 'types/libraryTab';

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

// Only locales whose alphabet can be represented safely by A-Z should use the
// Latin picker implicitly. Unknown locales remain on the legacy picker until a
// proper alphabet definition is added.
const LATIN_LOCALE_PREFIXES = new Set([
    'af', 'az', 'br', 'bs', 'ca', 'ch', 'cs', 'cy', 'da', 'de', 'en', 'eo',
    'es', 'et', 'eu', 'fi', 'fil', 'fo', 'fr', 'ga', 'gl', 'hr', 'hu', 'id',
    'is', 'it', 'lb', 'lt', 'lv', 'ms', 'mt', 'nb', 'nl', 'nn', 'pl', 'pt',
    'ro', 'sk', 'sl', 'sq', 'sv', 'sw', 'tr', 'uz', 'vi'
]);

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
    if (localeParts.includes('latn') || LATIN_LOCALE_PREFIXES.has(localeParts[0])) {
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

    const orderedInitials = [...new Set(enabled.flatMap(alphabet => alphabet.values))];
    const params: Record<string, string> = {
        nameInitialSortOrder: orderedInitials.join(',')
    };

    if (!selectedAlphabet) {
        return { query: {}, params };
    }

    if (selectedAlphabet === '#') {
        params.excludeNameInitials = orderedInitials.join(',');
        return { query: {}, params };
    }

    if (orderedInitials.includes(selectedAlphabet)) {
        params.nameInitials = selectedAlphabet;
    }

    return { query: {}, params };
};
'''
)

write(
    'src/apps/modern/features/libraries/utils/alphabet.test.ts',
    '''import { describe, expect, it } from 'vitest';

import { LibraryTab } from 'types/libraryTab';

import {
    getAlphabetFilter,
    getAlphabetNavigationSettings,
    getLocalizedAlphabetGroups,
    getPrimaryAlphabetDefinition
} from './alphabet';

const russian = {
    enabled: true,
    locale: 'ru-RU',
    additionalScripts: []
};

const greek = {
    enabled: true,
    locale: 'el-GR',
    additionalScripts: []
};

describe('localized alphabet navigation', () => {
    it('keeps Greek Ψ and Ω at the end of the native alphabet', () => {
        const values = getPrimaryAlphabetDefinition('el-GR')?.values ?? [];
        expect(values.at(-2)).toBe('Ψ');
        expect(values.at(-1)).toBe('Ω');
    });

    it('preserves the Russian alphabet order including Ё, Ч and Я', () => {
        const values = getPrimaryAlphabetDefinition('ru-RU')?.values ?? [];
        expect(values.indexOf('Ё')).toBe(values.indexOf('Е') + 1);
        expect(values.indexOf('Ч')).toBeGreaterThan(values.indexOf('Ц'));
        expect(values.at(-1)).toBe('Я');
    });

    it('keeps legacy filters unchanged while the global feature is disabled', () => {
        const filter = getAlphabetFilter(
            '#',
            { enabled: false, locale: 'ru-RU', additionalScripts: [] },
            LibraryTab.Movies
        );

        expect(filter.params).toBeUndefined();
        expect(filter.query).toEqual({ nameLessThan: 'A', nameStartsWith: undefined });
    });

    it('sends native initial ordering even when no bucket is selected', () => {
        const filter = getAlphabetFilter(null, russian, LibraryTab.Movies);
        const order = filter.params?.nameInitialSortOrder?.split(',') ?? [];

        expect(order[0]).toBe('А');
        expect(order.indexOf('Ч')).toBeGreaterThan(order.indexOf('Ц'));
        expect(order.at(-1)).toBe('Я');
    });

    it('filters Greek titles by their native initial', () => {
        const filter = getAlphabetFilter('Ω', greek, LibraryTab.Movies);
        expect(filter.params?.nameInitials).toBe('Ω');
    });

    it('uses # as Other while preserving the same native sort order', () => {
        const filter = getAlphabetFilter('#', russian, LibraryTab.Movies);

        expect(filter.params?.excludeNameInitials).toBe(filter.params?.nameInitialSortOrder);
        expect(filter.params?.excludeNameInitials).toContain('Ё');
    });

    it('appends Latin after the primary alphabet when Latn is enabled', () => {
        const settings = { ...greek, additionalScripts: ['Latn'] };
        const groups = getLocalizedAlphabetGroups(settings, LibraryTab.Movies);
        const filter = getAlphabetFilter(null, settings, LibraryTab.Movies);
        const order = filter.params?.nameInitialSortOrder?.split(',') ?? [];

        expect(groups).toHaveLength(2);
        expect(groups?.[0].values.at(-1)).toBe('Ω');
        expect(groups?.[1].values[0]).toBe('A');
        expect(order.indexOf('A')).toBeGreaterThan(order.indexOf('Ω'));
    });

    it('does not guess an ambiguous additional alphabet from a script code', () => {
        const groups = getLocalizedAlphabetGroups(
            { ...greek, additionalScripts: ['Cyrl'] },
            LibraryTab.Movies
        );
        expect(groups).toHaveLength(1);
    });

    it('uses Latin only for known Latin locales', () => {
        expect(getPrimaryAlphabetDefinition('en-US')?.id).toBe('latin');
        expect(getPrimaryAlphabetDefinition('hy-AM')).toBeUndefined();
        expect(getPrimaryAlphabetDefinition('ckb')).toBeUndefined();
        expect(getPrimaryAlphabetDefinition('te-IN')).toBeUndefined();
    });

    it('falls back to the legacy API for unsupported locales', () => {
        const filter = getAlphabetFilter(
            'A',
            { enabled: true, locale: 'hy-AM', additionalScripts: [] },
            LibraryTab.Movies
        );
        expect(filter.params).toBeUndefined();
        expect(filter.query.nameStartsWith).toBe('A');
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

    it('keeps endpoints without native-initial support on the legacy API path', () => {
        for (const viewType of [LibraryTab.Authors, LibraryTab.Channels, LibraryTab.SeriesTimers]) {
            const filter = getAlphabetFilter('O', russian, viewType);
            expect(filter.params).toBeUndefined();
            expect(filter.query.nameStartsWith).toBe('O');
        }
    });
});
'''
)

write(
    'src/apps/modern/features/libraries/components/AlphabetPicker.tsx',
    '''import React, { useCallback } from 'react';

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

const LETTER_VALUES = ['#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];

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
                    xs: '144px', // Extra small screens the AppBar wraps to 3 rows (128px) and we align top with 16px of spacing
                    sm: '96px' // Small screens the AppBar is 2 rows (96px) and we align center (no extra spacing)
                },
                bottom: 0,
                fontSize: '80%',
                display: 'flex',
                alignItems: {
                    xs: 'flex-start',
                    sm: 'center'
                },
                gap: localizedGroups ? 0.25 : undefined,
                // This should render under the main AppBar if overlapping
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
)

write(
    'src/apps/modern/features/libraries/components/GenresItemsContainer.tsx',
    '''import type { BaseItemKind } from '@jellyfin/sdk/lib/generated-client/models/base-item-kind';
import type { CollectionType } from '@jellyfin/sdk/lib/generated-client/models/collection-type';
import Box from '@mui/material/Box';
import React, { FC, useEffect, useMemo, useState } from 'react';
import { useIntersectionObserver } from 'usehooks-ts';

import NoItemsMessage from 'components/common/NoItemsMessage';
import Loading from 'components/loading/LoadingComponent';
import { useSystemInfo } from 'hooks/useSystemInfo';
import type { ParentId } from 'types/library';
import { LibraryTab } from 'types/libraryTab';

import { useGenres } from '../hooks/api/useGenres';
import { getAlphabetNavigationSettings, getLocalizedAlphabetGroups } from '../utils/alphabet';
import AlphabetPicker from './AlphabetPicker';
import GenresSectionContainer from './GenresSectionContainer';

interface GenresItemsContainerProps {
    parentId: ParentId;
    collectionType: CollectionType | undefined;
    itemType: BaseItemKind[];
}

const GenresItemsContainer: FC<GenresItemsContainerProps> = ({
    parentId,
    collectionType,
    itemType
}) => {
    const [alphabet, setAlphabet] = useState<string | null>();
    const { data: systemInfo } = useSystemInfo();
    const alphabetNavigationSettings = useMemo(
        () => getAlphabetNavigationSettings(systemInfo),
        [systemInfo]
    );
    const alphabetGroups = useMemo(
        () => getLocalizedAlphabetGroups(alphabetNavigationSettings, LibraryTab.Genres),
        [alphabetNavigationSettings]
    );
    const {
        isLoading,
        data,
        fetchNextPage,
        hasNextPage,
        isFetchingNextPage
    } = useGenres({
        parentId,
        includeItemTypes: itemType,
        alphabet,
        alphabetNavigationSettings
    });

    const genres = useMemo(
        () => data?.pages.flatMap((page) => page?.Items ?? []) ?? [],
        [data]
    );

    const { ref: sentinelRef, isIntersecting } = useIntersectionObserver({
        rootMargin: '200px'
    });

    useEffect(() => {
        if (isIntersecting && hasNextPage && !isFetchingNextPage) {
            void fetchNextPage();
        }
    }, [isIntersecting, hasNextPage, isFetchingNextPage, fetchNextPage]);

    // No genres at all (no letter filter active) - nothing to pick from
    if (!isLoading && !genres.length && alphabet == null) {
        return <NoItemsMessage message='MessageNoGenresAvailable' />;
    }

    const renderGenres = () => {
        if (isLoading) {
            return <Loading />;
        }

        if (!genres.length) {
            return <NoItemsMessage message='MessageNoGenresAvailable' />;
        }

        return (
            <>
                {genres.map((genre) => (
                    <GenresSectionContainer
                        key={genre.Id}
                        collectionType={collectionType}
                        parentId={parentId}
                        itemType={itemType}
                        genre={genre}
                    />
                ))}

                {hasNextPage && <Box ref={sentinelRef} sx={{ height: '1px' }} />}
                {isFetchingNextPage && <Loading />}
            </>
        );
    };

    return (
        <>
            <AlphabetPicker
                value={alphabet}
                onChange={setAlphabet}
                groups={alphabetGroups}
            />

            {renderGenres()}
        </>
    );
};

export default GenresItemsContainer;
'''
)

write(
    'src/apps/modern/features/libraries/hooks/api/useGenres.ts',
    '''import type { Api } from '@jellyfin/sdk/lib/api';
import type { GenreApiGetGenresRequest } from '@jellyfin/sdk/lib/generated-client/api/genre-api';
import type { BaseItemKind } from '@jellyfin/sdk/lib/generated-client/models/base-item-kind';
import { ItemSortBy } from '@jellyfin/sdk/lib/generated-client/models/item-sort-by';
import { SortOrder } from '@jellyfin/sdk/lib/generated-client/models/sort-order';
import { getGenreApi } from '@jellyfin/sdk/lib/utils/api/genre-api';
import { infiniteQueryOptions, useInfiniteQuery } from '@tanstack/react-query';
import type { AxiosRequestConfig } from 'axios';

import { useApi } from 'hooks/useApi';
import type { ItemDtoQueryResult } from 'types/base/models/item-dto-query-result';
import type { ParentId } from 'types/library';
import { LibraryTab } from 'types/libraryTab';

import {
    type AlphabetNavigationSettings,
    getAlphabetFilter,
    getAlphabetNavigationSettings
} from '../../utils/alphabet';

export const GENRES_PAGE_SIZE = 10;

interface GenresParams {
    parentId?: ParentId;
    includeItemTypes?: BaseItemKind[];
    /** Filter by the first letter of the genre name; '#' matches the Other bucket in localized mode. */
    alphabet?: string | null;
    alphabetNavigationSettings?: AlphabetNavigationSettings;
    userId?: string;
}

const fetchGenres = async (
    api: Api,
    params: GenreApiGetGenresRequest,
    options?: AxiosRequestConfig
) => {
    const response = await getGenreApi(api).getGenres(params, options);
    return response.data as ItemDtoQueryResult;
};

/** Query options for fetching genres. */
export const getGenresQuery = (
    api?: Api,
    params: GenresParams = {}
) => {
    const alphabetNavigationSettings = params.alphabetNavigationSettings
        ?? getAlphabetNavigationSettings();
    const alphabetFilter = getAlphabetFilter(
        params.alphabet,
        alphabetNavigationSettings,
        LibraryTab.Genres
    );

    return infiniteQueryOptions({
        queryKey: [
            'Genres',
            params.parentId,
            params.includeItemTypes,
            params.alphabet,
            alphabetNavigationSettings
        ],
        queryFn: ({ pageParam, signal }) => fetchGenres(
            api!,
            {
                userId: params.userId,
                includeItemTypes: params.includeItemTypes,
                parentId: params.parentId ?? undefined,
                sortBy: [ItemSortBy.SortName],
                sortOrder: [SortOrder.Ascending],
                ...alphabetFilter.query,
                enableTotalRecordCount: false,
                startIndex: pageParam * GENRES_PAGE_SIZE,
                limit: GENRES_PAGE_SIZE
            },
            {
                signal,
                params: alphabetFilter.params
            }
        ),
        initialPageParam: 0,
        // Stop once a page returns fewer items than requested (cheaper than enabling total record count)
        getNextPageParam: (lastPage, allPages) =>
            (lastPage?.Items?.length ?? 0) < GENRES_PAGE_SIZE ? undefined : allPages.length,
        enabled: !!api && !!params.userId && !!params.parentId
    });
};

/** Hook for fetching genres. */
export const useGenres = (params?: GenresParams) => {
    const { api, user } = useApi();
    return useInfiniteQuery(getGenresQuery(
        api,
        {
            ...params,
            userId: params?.userId || user?.Id
        }
    ));
};
'''
)

# Keep the Dashboard's current structure but preserve additional scripts that
# this Web version does not yet expose in its UI.
settings_path = root / 'src/apps/dashboard/routes/settings/index.tsx'
settings = settings_path.read_text(encoding='utf-8')
old_settings = """    localizedAlphabetConfig.EnableLocalizedAlphabetNavigation =\n        formData.get('EnableLocalizedAlphabetNavigation')?.toString() === 'on';\n    localizedAlphabetConfig.LocalizedAlphabetAdditionalScripts =\n        formData.get('IncludeLatinAlphabet')?.toString() === 'on' ? ['Latn'] : [];\n"""
new_settings = """    localizedAlphabetConfig.EnableLocalizedAlphabetNavigation =\n        formData.get('EnableLocalizedAlphabetNavigation')?.toString() === 'on';\n    const additionalScripts = (localizedAlphabetConfig.LocalizedAlphabetAdditionalScripts ?? [])\n        .filter(script => script !== 'Latn');\n    localizedAlphabetConfig.LocalizedAlphabetAdditionalScripts =\n        formData.get('IncludeLatinAlphabet')?.toString() === 'on' ?\n            [...additionalScripts, 'Latn'] :\n            additionalScripts;\n"""
if old_settings not in settings:
    raise SystemExit('Expected localized alphabet settings block was not found')
settings_path.write_text(settings.replace(old_settings, new_settings), encoding='utf-8')

# The helper now receives just the selected alphabet, which also makes it
# reusable by the standalone Genres query.
fetch_path = root / 'src/hooks/useFetchItems.ts'
fetch_text = fetch_path.read_text(encoding='utf-8')
old_filter_call = """        const alphabetFilter = getAlphabetFilter(\n            libraryViewSettings,\n            alphabetNavigationSettings,\n            viewType\n        );\n"""
new_filter_call = """        const alphabetFilter = getAlphabetFilter(\n            libraryViewSettings.Alphabet,\n            alphabetNavigationSettings,\n            viewType\n        );\n"""
if old_filter_call not in fetch_text:
    raise SystemExit('Expected getAlphabetFilter call was not found')
fetch_path.write_text(fetch_text.replace(old_filter_call, new_filter_call), encoding='utf-8')

# Ensure source-language keys are present; all non-English translations are
# intentionally left to Weblate per CONTRIBUTING.md.
en_path = root / 'src/strings/en-us.json'
en_text = en_path.read_text(encoding='utf-8')
for key in ('UseLocalizedAlphabetNavigation', 'IncludeLatinAlphabet'):
    if f'"{key}"' not in en_text:
        raise SystemExit(f'Missing expected source-language key: {key}')
