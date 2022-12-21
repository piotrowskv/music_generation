import { afterEach, describe, vi } from 'vitest'
import { ThemeMode, useThemeContext } from '../../../stores/ThemeContext'
import { cleanup, render, screen } from '../../test-utils'

describe('ThemeContext', () => {
    afterEach(() => {
        vi.resetAllMocks()
        cleanup()
    })

    function renderTest() {
        function TestComponent() {
            const theme = useThemeContext()

            return (
                <>
                    {(Object.keys(theme) as (keyof typeof theme)[]).map(e => (
                        <div key={e} data-testid={e}>
                            {theme[e].toString()}
                        </div>
                    ))}
                </>
            )
        }

        render(<TestComponent />)
    }

    test('has correct default values', () => {
        renderTest()

        expect(screen.getByTestId('mode')).toHaveTextContent(
            ThemeMode.system.toString()
        )
    })
})
