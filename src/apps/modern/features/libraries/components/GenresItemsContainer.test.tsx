import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useSystemInfo } from 'hooks/useSystemInfo';

import { useGenres } from '../hooks/api/useGenres';
import GenresItemsContainer from './GenresItemsContainer';

vi.mock('hooks/useSystemInfo', () => ({ useSystemInfo: vi.fn() }));
vi.mock('../hooks/api/useGenres', () => ({ useGenres: vi.fn() }));
vi.mock('usehooks-ts', () => ({
    useIntersectionObserver: () => ({ ref: vi.fn(), isIntersecting: false })
}));
vi.mock('components/common/NoItemsMessage', () => ({ default: () => 'No genres' }));
vi.mock('components/loading/LoadingComponent', () => ({ default: () => 'Loading' }));
vi.mock('./AlphabetPicker', () => ({ default: () => null }));
vi.mock('./GenresSectionContainer', () => ({ default: () => null }));

describe('GenresItemsContainer', () => {
    beforeEach(() => {
        vi.mocked(useGenres).mockReturnValue({
            data: { pages: [] },
            isLoading: false,
            hasNextPage: false,
            isFetchingNextPage: false,
            fetchNextPage: vi.fn()
        } as unknown as ReturnType<typeof useGenres>);
    });

    it.each([
        [true, false, 'Loading'],
        [false, true, 'No genres']
    ])('handles pending SystemInfo: %s', (isPending, enabled, expected) => {
        vi.mocked(useSystemInfo).mockReturnValue({
            data: undefined,
            isPending
        } as ReturnType<typeof useSystemInfo>);

        const markup = renderToStaticMarkup(
            <GenresItemsContainer parentId='library' collectionType={undefined} itemType={[]} />
        );

        expect(markup).toBe(expected);
        expect(useGenres).toHaveBeenLastCalledWith(expect.objectContaining({
            enabled,
            alphabetNavigationSettings: { enabled: false, locale: '', additionalScripts: [] }
        }));
    });
});
