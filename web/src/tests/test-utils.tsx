import { findByTestId, render, RenderOptions } from '@testing-library/react'
import React from 'react'
import { HashRouter } from 'react-router-dom'
import { ThemeProvider } from '../stores/ThemeContext'
import { DataTestId } from '../utils/testing'

const AllProviders: React.FC<{ children: React.ReactNode }> = ({
    children,
}) => {
    return (
        <ThemeProvider>
            <HashRouter>{children}</HashRouter>
        </ThemeProvider>
    )
}

const customRender = (
    ui: React.ReactElement,
    options?: Omit<RenderOptions, 'queries'>
) =>
    render(ui, {
        wrapper: AllProviders,
        ...options,
    }) as unknown as ReturnType<typeof render> & {
        findByTestId: (
            k: keyof typeof DataTestId
        ) => ReturnType<typeof findByTestId>
    }

export * from '@testing-library/react'
export { customRender as render }
