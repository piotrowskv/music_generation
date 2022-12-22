import { expect, vi } from 'vitest'
import ErrorMessage from '../../components/ErrorMessage'
import { cleanup, render, screen } from '../test-utils'

describe('ErrorMessage', () => {
    afterEach(() => {
        cleanup()
    })

    test('renders message', async () => {
        const f = vi.fn()
        render(<ErrorMessage onRetry={f}>Failed to load models</ErrorMessage>)

        expect(screen.findByText('Failed to load models')).toBeTruthy()
    })

    test('renders error when present', async () => {
        const f = vi.fn()
        render(
            <ErrorMessage onRetry={f} error={'I am an error'}>
                Failed to load models
            </ErrorMessage>
        )

        expect(screen.findByText('I am an error')).toBeTruthy()
    })

    test('calls callback on refresh', async () => {
        const f = vi.fn()
        render(<ErrorMessage onRetry={f}>Failed to load models</ErrorMessage>)
        ;(await screen.findByRole('button')).click()

        expect(f).toHaveBeenCalledOnce()
    })
})
