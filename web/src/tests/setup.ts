import '@testing-library/jest-dom'
import 'isomorphic-fetch'
import { vi } from 'vitest'

vi.mock('../utils/config.ts', () => ({
    apiUrl: 'something',
}))

vi.mock('../api/ApiClient.ts')

Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
    })),
})

export {}
