import {
    createContext,
    FC,
    ReactNode,
    useContext,
    useEffect,
    useState,
} from 'react'

export enum ThemeMode {
    system,
    light,
    dark,
}

export enum ResolvedTheme {
    light,
    dark,
}

const ThemeContext = createContext<{
    mode: ResolvedTheme
    changeMode: (mode: ThemeMode) => void
}>(null!)

const localStorageKey = 'theme-mode'

export const ThemeProvider: FC<{ children: ReactNode }> = ({ children }) => {
    const [mode, setMode] = useState(() => {
        const saved = localStorage.getItem(localStorageKey)
        if (saved) {
            return ThemeMode[saved as keyof typeof ThemeMode]
        } else {
            return ThemeMode.system
        }
    })

    useEffect(() => {
        localStorage.setItem(localStorageKey, ThemeMode[mode])
    }, [mode])

    const resolved = (() => {
        switch (mode) {
            case ThemeMode.system:
                if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                    return ResolvedTheme.dark
                } else {
                    return ResolvedTheme.light
                }
            case ThemeMode.light:
                return ResolvedTheme.light
            case ThemeMode.dark:
                return ResolvedTheme.dark
        }
    })()

    return (
        <ThemeContext.Provider value={{ mode: resolved, changeMode: setMode }}>
            {children}
        </ThemeContext.Provider>
    )
}

export const useThemeContext = () => useContext(ThemeContext)
