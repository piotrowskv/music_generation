import { FC } from 'react'
import Moon from '../assets/Moon'
import Sun from '../assets/Sun'
import {
    ResolvedTheme,
    ThemeMode,
    useThemeContext,
} from '../stores/ThemeContext'

const ThemeSwitch: FC = () => {
    const { mode, changeMode } = useThemeContext()

    const Icon = mode === ResolvedTheme.dark ? Moon : Sun

    return (
        <button
            className="h-9 w-9"
            onClick={() =>
                changeMode(
                    mode === ResolvedTheme.dark
                        ? ThemeMode.light
                        : ThemeMode.dark
                )
            }
        >
            <Icon className="h-9 w-9 hover:fill-gray dark:fill-white hover:dark:fill-gray" />
        </button>
    )
}

export default ThemeSwitch
