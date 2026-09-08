import { Api } from '@jellyfin/sdk/lib/api';
import { BaseItemKind } from '@jellyfin/sdk/lib/generated-client/models/base-item-kind';
import { InfiniteQueryObserver, QueryClient } from '@tanstack/react-query';
import axios, { type InternalAxiosRequestConfig } from 'axios';
import { describe, expect, it, vi } from 'vitest';

import { GENRES_PAGE_SIZE, getGenresQuery } from './useGenres';

vi.mock('hooks/useApi', () => ({ useApi: vi.fn() }));

const settings = { enabled: true, locale: 'el-GR', additionalScripts: ['Latn'] };

function createApi() {
    const requests: URL[] = [];
    const client = axios.create({
        adapter: async (config: InternalAxiosRequestConfig) => {
            requests.push(new URL(axios.getUri(config)));
            const count = requests.length === 1 ? GENRES_PAGE_SIZE : 1;
            return {
                data: { Items: Array.from({ length: count }, (_, index) => ({ Id: `${requests.length}-${index}` })) },
                status: 200,
                statusText: 'OK',
                headers: {},
                config
            };
        }
    });
    const api = new Api('https://jellyfin.example', { name: 'test', version: '1' }, { name: 'test', id: 'test' }, undefined, client);
    return { api, requests };
}

describe('genre alphabet queries', () => {
    it('keeps cached pages separate for different users', async () => {
        const { api, requests } = createApi();
        const client = new QueryClient();
        try {
            for (const userId of ['first-user', 'second-user']) {
                await client.fetchInfiniteQuery({ ...getGenresQuery(api, { parentId: 'library', userId }), staleTime: Infinity });
            }
            expect(requests.map(url => url.searchParams.get('userId'))).toEqual(['first-user', 'second-user']);
        } finally {
            client.clear();
        }
    });

    it.each([
        ['Α', 'nameInitials', 'Α,Ά'],
        ['#', 'excludeNameInitials', 'Α'],
        [null, 'nameInitialSortOrder', 'Α|Ά,Β']
    ])('preserves SDK parameters and native filtering across pages: %s', async (alphabet, parameter, expected) => {
        const { api, requests } = createApi();
        const client = new QueryClient();
        const observer = new InfiniteQueryObserver(client, getGenresQuery(api, { parentId: 'library', userId: 'user', includeItemTypes: [BaseItemKind.Movie], alphabet, alphabetNavigationSettings: settings }));
        try {
            await observer.refetch();
            expect(observer.getCurrentResult().hasNextPage).toBe(true);
            await observer.fetchNextPage();
            expect(observer.getCurrentResult().hasNextPage).toBe(false);
            expect(requests).toHaveLength(2);
            requests.forEach((url, index) => {
                expect(url.pathname).toBe('/Genres');
                expect(url.searchParams.get('userId')).toBe('user');
                expect(url.searchParams.get('parentId')).toBe('library');
                expect(url.searchParams.get('includeItemTypes')).toBe('Movie');
                expect(url.searchParams.get('sortBy')).toBe('SortName');
                expect(url.searchParams.get('sortOrder')).toBe('Ascending');
                expect(url.searchParams.get('startIndex')).toBe(String(index * GENRES_PAGE_SIZE));
                expect(url.searchParams.get('limit')).toBe(String(GENRES_PAGE_SIZE));
                expect(url.searchParams.get('enableTotalRecordCount')).toBe('false');
                expect(url.searchParams.get(parameter ?? '')).toContain(expected);
                expect(url.searchParams.has('nameStartsWith')).toBe(false);
                expect(url.searchParams.has('nameLessThan')).toBe(false);
            });
        } finally {
            observer.destroy();
            client.clear();
        }
    });

    it('uses legacy SDK filtering when localized navigation is disabled', async () => {
        const { api, requests } = createApi();
        const client = new QueryClient();
        try {
            await client.fetchInfiniteQuery(getGenresQuery(api, { parentId: 'library', userId: 'user', alphabet: '#', alphabetNavigationSettings: { ...settings, enabled: false } }));
            expect(requests[0].searchParams.get('nameLessThan')).toBe('A');
            for (const parameter of ['nameInitials', 'excludeNameInitials', 'nameInitialSortOrder']) {
                expect(requests[0].searchParams.has(parameter)).toBe(false);
            }
        } finally {
            client.clear();
        }
    });
});
