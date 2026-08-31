import { describe, expect, it } from 'vitest';

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

    it('preserves the Russian alphabet order including Ё, Й, Ч and Я', () => {
        const values = getPrimaryAlphabetDefinition('ru-RU')?.values ?? [];
        expect(values.indexOf('Ё')).toBe(values.indexOf('Е') + 1);
        expect(values.indexOf('Й')).toBe(values.indexOf('И') + 1);
        expect(values.indexOf('Ч')).toBeGreaterThan(values.indexOf('Ц'));
        expect(values.at(-1)).toBe('Я');
    });

    it('preserves Ukrainian-specific letters in their alphabet order', () => {
        const values = getPrimaryAlphabetDefinition('uk-UA')?.values ?? [];
        expect(values.indexOf('Ґ')).toBe(values.indexOf('Г') + 1);
        expect(values.indexOf('Є')).toBe(values.indexOf('Е') + 1);
        expect(values.indexOf('І')).toBe(values.indexOf('И') + 1);
        expect(values.indexOf('Ї')).toBe(values.indexOf('І') + 1);
    });

    it('preserves Belarusian Ў and Bulgarian hard sign ordering', () => {
        const belarusian = getPrimaryAlphabetDefinition('be-BY')?.values ?? [];
        const bulgarian = getPrimaryAlphabetDefinition('bg-BG')?.values ?? [];
        expect(belarusian.indexOf('Ў')).toBe(belarusian.indexOf('У') + 1);
        expect(bulgarian.indexOf('Ъ')).toBeGreaterThan(bulgarian.indexOf('Щ'));
        expect(bulgarian.at(-1)).toBe('Я');
    });

    it('keeps Bulgarian grave-marked И in the И bucket', () => {
        const bulgarian = { enabled: true, locale: 'bg-BG', additionalScripts: [] };
        const selected = getAlphabetFilter('И', bulgarian, LibraryTab.Movies);
        const order = getAlphabetFilter(null, bulgarian, LibraryTab.Movies)
            .params?.nameInitialSortOrder?.split(',') ?? [];

        expect(selected.params?.nameInitials?.split(',')).toEqual(['И', 'Ѝ']);
        expect(order).toContain('И|Ѝ');
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

    it('sends native initial ordering only when no bucket is selected', () => {
        const filter = getAlphabetFilter(null, russian, LibraryTab.Movies);
        const order = filter.params?.nameInitialSortOrder?.split(',') ?? [];

        expect(order[0]).toBe('А');
        expect(order.indexOf('Ч')).toBeGreaterThan(order.indexOf('Ц'));
        expect(order.at(-1)).toBe('Я');
    });

    it('maps Greek accented initials to their base navigation bucket', () => {
        const filter = getAlphabetFilter('Α', greek, LibraryTab.Movies);
        const initials = filter.params?.nameInitials?.split(',') ?? [];

        expect(initials).toEqual(['Α', 'Ά']);
        expect(filter.params?.nameInitialSortOrder).toBeUndefined();
    });

    it('serializes Greek aliases as one sorting rank per visual bucket', () => {
        const filter = getAlphabetFilter(null, greek, LibraryTab.Movies);
        const order = filter.params?.nameInitialSortOrder?.split(',') ?? [];

        expect(order[0]).toBe('Α|Ά');
        expect(order[1]).toBe('Β');
        expect(order).toContain('Ι|Ί|Ϊ|ΐ');
        expect(order).toContain('Σ|ς');
        expect(order).toContain('Υ|Ύ|Ϋ|ΰ');
        expect(order.at(-1)).toBe('Ω|Ώ');
    });

    it('selecting a Greek alias resolves to the same visual bucket', () => {
        const filter = getAlphabetFilter('ΐ', greek, LibraryTab.Movies);
        expect(filter.params?.nameInitials?.split(',')).toEqual(['Ι', 'Ί', 'Ϊ', 'ΐ']);
        expect(filter.params?.nameInitialSortOrder).toBeUndefined();
    });

    it('uses # as Other without applying native group ordering inside the bucket', () => {
        const filter = getAlphabetFilter('#', greek, LibraryTab.Movies);
        const excluded = filter.params?.excludeNameInitials?.split(',') ?? [];

        expect(excluded).toContain('Α');
        expect(excluded).toContain('Ά');
        expect(excluded).toContain('Ω');
        expect(excluded).toContain('Ώ');
        expect(filter.params?.nameInitialSortOrder).toBeUndefined();
    });

    it('appends Latin after the primary alphabet when Latn is enabled', () => {
        const settings = { ...greek, additionalScripts: ['Latn'] };
        const groups = getLocalizedAlphabetGroups(settings, LibraryTab.Movies);
        const filter = getAlphabetFilter(null, settings, LibraryTab.Movies);
        const order = filter.params?.nameInitialSortOrder?.split(',') ?? [];

        expect(groups).toHaveLength(2);
        expect(groups?.[0].values.at(-1)).toBe('Ω');
        expect(groups?.[1].values[0]).toBe('A');
        expect(order.indexOf('A')).toBeGreaterThan(order.indexOf('Ω|Ώ'));
    });

    it('does not guess an ambiguous additional alphabet from a script code', () => {
        const groups = getLocalizedAlphabetGroups(
            { ...greek, additionalScripts: ['Cyrl'] },
            LibraryTab.Movies
        );
        expect(groups).toHaveLength(1);
    });

    it('keeps ordinary Latin locales on the legacy picker', () => {
        expect(getPrimaryAlphabetDefinition('en-US')).toBeUndefined();
        expect(getPrimaryAlphabetDefinition('fr-FR')).toBeUndefined();
        expect(getPrimaryAlphabetDefinition('sv-SE')).toBeUndefined();
        expect(getPrimaryAlphabetDefinition('en-Latn-US')?.id).toBe('latin');
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
