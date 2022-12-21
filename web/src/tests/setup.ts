import '@testing-library/jest-dom'
import 'isomorphic-fetch'
import { vi } from 'vitest'

vi.mock('../utils/config.ts', () => ({
    apiUrl: 'something',
}))

vi.mock('../api/ApiClient.ts')

export {}
