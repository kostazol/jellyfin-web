import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';

import AlphabetPicker from './AlphabetPicker';

const renderPicker = (groups?: { id: string; values: string[] }[]) => {
    const container = document.createElement('div');
    container.innerHTML = renderToStaticMarkup(<AlphabetPicker groups={groups} onChange={vi.fn()} />);
    return container;
};

describe('AlphabetPicker', () => {
    it.each([undefined, []])('keeps the legacy picker when groups are %s', groups => {
        const container = renderPicker(groups);
        const buttons = Array.from(container.querySelectorAll('button'), button => button.textContent);

        expect(buttons).toEqual(['#', ...'ABCDEFGHIJKLMNOPQRSTUVWXYZ']);
        expect(container.querySelectorAll('[role="group"]')).toHaveLength(1);
    });

    it('shows Other only once before the localized alphabets', () => {
        const container = renderPicker([
            { id: 'greek', values: ['Α', 'Β'] },
            { id: 'latin', values: ['A', 'B'] }
        ]);
        const buttons = Array.from(container.querySelectorAll('button'), button => button.textContent);

        expect(buttons).toEqual(['#', 'Α', 'Β', 'A', 'B']);
        expect(container.querySelectorAll('[role="group"]')).toHaveLength(2);
    });
});
