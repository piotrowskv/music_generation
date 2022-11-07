import { afterEach, describe, it, vi } from 'vitest'

describe('Dummy group', () => {
    afterEach(() => {
        vi.resetAllMocks()
    })

    it('dummy test', () => {
        expect(true).toBe(true)
    })
})
