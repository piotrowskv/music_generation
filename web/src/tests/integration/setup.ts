import { vi } from 'vitest'

const testUrl = import.meta.env['TEST_URL']

const { ApiClient } = await vi.importActual<
    typeof import('../../api/ApiClient')
>('../../api/ApiClient')

export const apiClient = new ApiClient(testUrl)

export const testUrlDescribe = testUrl ? describe : describe.skip
